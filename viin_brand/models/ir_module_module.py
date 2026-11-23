import ast
import functools
import os
from collections import defaultdict
from contextlib import suppress

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.fields import Domain
from odoo.http import request
from odoo.tools import SQL, config, file_open, file_path
from odoo.tools.translate import ParsedTranslation, TranslationImporter, get_po_paths, translation_file_reader

from ..tools import debrand_exception

# The modules that sell Odoo IAP credits and that no other module depends on: a new database does not
# install them and the user interface does not offer to.
IAP_SERVICE_MODULES = (
    'crm_iap_enrich', 'crm_iap_mine', 'website_crm_iap_reveal', 'snailmail', 'snailmail_account',
)
# Their rows exist before they are installed, so the guard below knows them by name.
IAP_MODULES = ('iap', 'iap_crm', 'iap_mail') + IAP_SERVICE_MODULES

# The Apps lists that hide the Enterprise-only module stubs. A module that adds an Apps list of its
# own extends ``_get_apps_actions``.
APPS_ACTION_XMLIDS = ('base.open_module_tree',)


def _is_to_buy_condition(condition):
    return condition.field_expr == 'to_buy'


def _hide_enterprise_stubs(domain):
    """Add the condition that hides the Enterprise-only module stubs, once.

    :param Domain domain: the domain of a module list
    :return: ``domain`` itself when it already hides the stubs, else the domain with the condition
    """
    if any(_is_to_buy_condition(c) for c in domain.iter_conditions()):
        return domain
    return Domain('to_buy', '=', False) & domain


def _is_branding_module(module_name):
    return module_name == 'viin_brand' or module_name.startswith('viin_brand_')


def _terms_of(field, value):
    """Return the translatable terms of the value of a ``model_terms`` field, in order."""
    return ParsedTranslation(field, value).terms if value else []


def _catalog_texts(entries, lang):
    """Return the English sources of catalog entries and their translations in ``lang``."""
    texts = {entry[2] for entry in entries}
    texts.update(text for _module, _xmlid, _source, row_lang, text in entries if row_lang == lang and text)
    return texts


@functools.lru_cache(maxsize=256)
def _parse_catalog(path, mtime_ns, size):
    """Return the entries a catalog file gives records, by external id.

    A catalog file is static while the server runs: it is parsed once per process and again when
    its modification time or its size (``mtime_ns`` and ``size``, part of the cache key) changes.
    The cache holds the parsed catalogs of the least recently read 256 files.

    :return: ``{xmlid: ((model, field, xmlid), English source, translation), ...}``
    """
    index = defaultdict(list)
    with file_open(path, 'rb') as po_file:
        for row in translation_file_reader(po_file, 'po'):
            if row['type'] in ('model', 'model_terms'):
                xmlid = '%s.%s' % (row['module'], row['imd_name'])
                key = (row['imd_model'], row['name'].split(',')[1], xmlid)
                index[xmlid].append((key, row['src'], row['value']))
    return {xmlid: tuple(rows) for xmlid, rows in index.items()}


def _get_pot_path(module_name):
    """Return the path of the catalog template of a module, ``None`` when it has none."""
    with suppress(FileNotFoundError):
        return file_path('%s/i18n/%s.pot' % (module_name, module_name))
    return None


def _translations_of(branding, entries, model, field_name, source, lang):
    """Return the texts that translate ``source`` in ``lang``, with the one a record takes.

    :param branding: ``{(model, field, English, lang): {translation}}`` of the branding catalogs
    :param entries: the entries of the catalogs naming the record (``_read_stock_texts``)
    :return: ``(translations, target)``: the translations of the branding catalogs and of the
        catalogs naming the record, and the one a record that holds none of them takes: a branding
        one first, then one of the record's catalogs, else ``source`` itself
    """
    own = branding.get((model, field_name, source, lang), set())
    stock = {text for _module, _xmlid, src, row_lang, text in entries if src == source and row_lang == lang and text}
    translations = own | stock
    return translations, min(own or stock or {source})


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _update_domain_for_action(self):
        """Hide the Enterprise-only module stubs (``to_buy``) from the Apps lists.

        The condition is ANDed with whatever domain an action already has (website adds one that
        hides themes) and added only once, so reloading data never stacks it. An Apps action of a
        module that is not installed is skipped.
        """
        for action in self._get_apps_actions():
            domain = Domain(ast.literal_eval(action.domain or '[]'))
            hidden = _hide_enterprise_stubs(domain)
            if hidden is not domain:
                action.domain = repr(hidden)

    @api.model
    def _restore_domain_for_action(self):
        """Drop only the ``to_buy`` condition, leaving the domain other modules put on the actions."""
        for action in self._get_apps_actions():
            if not action.domain:
                continue
            domain = Domain(ast.literal_eval(action.domain)).map_conditions(
                lambda c: Domain.TRUE if _is_to_buy_condition(c) else c,
            )
            action.domain = False if domain.is_true() else repr(domain)

    @api.model
    def _get_apps_actions(self):
        actions = self.env['ir.actions.act_window']
        for xmlid in APPS_ACTION_XMLIDS:
            actions |= self.env.ref(xmlid, raise_if_not_found=False) or actions.browse()
        return actions

    @api.model
    def _load_module_terms(self, modules, langs, overwrite=False):
        """Let a branding catalog win over the stock translation of what it re-words.

        The loader keeps a translation a record already holds, so a record whose
        English a branding module (``viin_brand`` or ``viin_brand_*``) re-words keeps
        the stock wording in a language that came before the branding catalog:
        loaded with the modules, before an update, or added later. The catalog of
        each branding module of ``modules`` is applied by
        :meth:`_reapply_noupdate_translations`, which keeps a text a user wrote.
        Where no catalog translates the English of a branding module, the record shows
        that English (:meth:`_apply_branding_english`).
        """
        super()._load_module_terms(modules, langs, overwrite=overwrite)
        branding_modules = [module_name for module_name in modules if _is_branding_module(module_name)]
        for module_name in branding_modules:
            self._reapply_noupdate_translations(module_name, langs)
        self._apply_branding_english(modules, langs)

    @api.model
    def _reapply_noupdate_translations(self, module_name, langs=None):
        """Apply the translation catalog of a module to the records it re-words, ``noupdate`` ones included.

        The loader of a catalog never replaces an existing translation of a record whose external
        id is ``noupdate``, nor one that a catalog of another module naming the record filled in
        first, so a language installed before the module keeps the stock wording of such a record,
        product name included. The entries of the module's own catalog are applied to those records
        in the given languages; running it again changes nothing.

        A record named by several modules (a field that each of them declares) takes, among the
        entries the catalogs of those modules give it, the one whose English source is the
        record's English: this catalog's entry when its source is that English, otherwise the
        entry of the catalog, a branding one first, that translates the English the record holds;
        an entry of that English with an empty msgstr, where no entry has a translation, reads as
        the English itself and replaces a translation the catalogs know.

        A translation is replaced only while it is made of texts the catalogs of the record know
        (their English and their translations), the English text of the record, or the texts of
        this catalog: a text a user wrote is kept. A value translated term by term is tested on
        its terms, markup apart, and keeps the stock translation of a term this catalog lacks.

        The catalogs of the record's own module and of this module settle most records; those of
        the other modules naming a record are read only for a record they leave undecided.

        :param str module_name: the module whose catalog is applied
        :param langs: language codes; ``None`` applies every installed language
        """
        if langs is None:
            langs = [code for code, _name in self.env['res.lang'].get_installed()]
        langs = [code for code in langs if code != 'en_US']
        catalog = TranslationImporter(self.env.cr, verbose=False)
        for lang in langs:
            for path in get_po_paths(module_name, lang):
                catalog.load_file(path, lang)
        xmlids = self._get_catalog_xmlids(catalog)
        if not xmlids:
            return
        catalog_modules = {xmlid.split('.', 1)[0] for xmlid in xmlids} | {module_name}
        stock = self._read_stock_texts(catalog_modules, langs, xmlids)
        self.env.flush_all()
        selected = TranslationImporter(self.env.cr, verbose=False)
        pending = []
        for model, fields in catalog.model_translations.items():
            for field_name, records in fields.items():
                for xmlid, values in records.items():
                    record = self._get_catalog_record(xmlids, xmlid, model)
                    if record and not self._select_plain(
                        selected, module_name, record, field_name, xmlid, values, stock[model, field_name, xmlid],
                        undecided=True,
                    ):
                        pending.append(('plain', record, field_name, xmlid, values))
        for model, fields in catalog.model_terms_translations.items():
            for field_name, records in fields.items():
                for xmlid, terms in records.items():
                    record = self._get_catalog_record(xmlids, xmlid, model)
                    if record and not self._select_terms(
                        selected, record, field_name, xmlid, terms, stock[model, field_name, xmlid], undecided=True,
                    ):
                        pending.append(('terms', record, field_name, xmlid, terms))
        if pending:
            aliases = self._get_record_xmlids({xmlid for _kind, _record, _field, xmlid, _values in pending})
            named = set().union(*aliases.values())
            stock = self._read_stock_texts({alias.split('.', 1)[0] for alias in named} | catalog_modules, langs, named)
            for kind, record, field_name, xmlid, values in pending:
                entries = [entry for alias in aliases[xmlid] for entry in stock[record._name, field_name, alias]]
                if kind == 'plain':
                    self._select_plain(selected, module_name, record, field_name, xmlid, values, entries)
                else:
                    self._select_terms(selected, record, field_name, xmlid, values, entries)
        selected.save(force_overwrite=True)

    @api.model
    def _select_plain(self, selected, module_name, record, field_name, xmlid, values, entries, undecided=False):
        """Select the translations of a plain field a record takes, into the ``selected`` importer.

        :param dict values: ``{lang: translation}`` the catalog of ``module_name`` gives the record
        :param entries: the catalog entries known for the record (:meth:`_read_stock_texts`)
        :param bool undecided: leave a language undecided, and return ``False``, unless the
            catalog's own entry translates the record's English and settles it from ``entries``
        :return: whether every language was decided
        """
        english = record.with_context(lang='en_US')[field_name]
        decided = True
        for lang, value in values.items():
            if undecided and not self._is_own_translation(module_name, xmlid, entries, lang, value, english):
                decided = False
                continue
            target = self._select_translation(module_name, xmlid, entries, lang, value, english)
            stored = record.with_context(lang=lang)[field_name]
            if target and stored == target:
                continue
            known = {english, value} | _catalog_texts(entries, lang)
            if target and (not stored or stored in known):
                selected.model_translations[record._name][field_name][xmlid][lang] = target
            elif undecided:
                decided = False
        return decided

    @api.model
    def _select_terms(self, selected, record, field_name, xmlid, terms, entries, undecided=False):
        """Select the term translations a record takes, into the ``selected`` importer.

        :param dict terms: ``{English term: {lang: translation}}`` of the catalog applied
        :param entries: the catalog entries known for the record (:meth:`_read_stock_texts`)
        :param bool undecided: return ``False`` instead of deciding when the entries may not
            hold every catalog text the record can carry
        :return: whether every language was decided
        """
        field = record._fields[field_name]
        english_terms = _terms_of(field, record.with_context(lang='en_US')[field_name])
        decided = True
        for lang in {lang for values in terms.values() for lang in values}:
            stored_terms = _terms_of(field, record.with_context(lang=lang)[field_name])
            applied = len(english_terms) == len(stored_terms) and all(
                terms.get(term, {}).get(lang, translated) == translated
                for term, translated in zip(english_terms, stored_terms)
            )
            if applied:
                continue
            known = set(english_terms) | set(terms) | _catalog_texts(entries, lang)
            known.update(values[lang] for values in terms.values() if lang in values)
            if known.issuperset(stored_terms):
                selected_terms = selected.model_terms_translations[record._name][field_name][xmlid]
                for source, values in terms.items():
                    if lang in values:
                        selected_terms[source][lang] = values[lang]
            elif undecided:
                decided = False
        return decided

    @api.model
    def _select_translation(self, module_name, xmlid, entries, lang, value, english):
        """Return the translation a record holding ``english`` takes in ``lang``, ``None`` when unknown.

        The catalog's own value applies when the entry it comes from (this module, this external
        id, this language) translates ``english``. Otherwise the translation is the one the entries
        of the record's English give, a branding catalog's first; when none of them has a
        translation, an entry of that English with an empty msgstr gives ``english`` itself.

        :param str module_name: the branding module whose catalog gives ``value``
        :param str xmlid: the external id the catalog of ``module_name`` names the record by
        :param entries: the entries of the catalogs naming the record (:meth:`_read_stock_texts`)
        :param str value: the translation the catalog of ``module_name`` gives the record
        """
        if self._is_own_translation(module_name, xmlid, entries, lang, value, english):
            return value
        matching = [
            (module, text) for module, _alias, source, row_lang, text in entries
            if source == english and row_lang == lang and text
        ] or [
            # a catalog that leaves the msgstr empty translates the source to itself
            (module, english) for module, _alias, source, row_lang, text in entries
            if source == english and row_lang == lang
        ]
        branding = {text for module, text in matching if _is_branding_module(module)}
        candidates = branding or {text for _module, text in matching}
        return candidates.pop() if len(candidates) == 1 else None

    @api.model
    def _is_own_translation(self, module_name, xmlid, entries, lang, value, english):
        """Return whether the entry ``value`` comes from translates ``english``.

        That entry is the one of the catalog of ``module_name`` naming ``xmlid`` in ``lang``
        with ``value`` as translation; another entry of the same catalog (another external id
        of the record, another language) does not tell the source of ``value``.
        """
        return any(
            module == module_name and alias == xmlid and row_lang == lang and text == value and source == english
            for module, alias, source, row_lang, text in entries
        )

    @api.model
    def _read_stock_texts(self, module_names, langs, xmlids):
        """Read the entries the catalogs of modules give records, translated or not.

        A catalog file is parsed once per process (:func:`_parse_catalog`).

        :param module_names: the modules whose PO files are read
        :param langs: language codes
        :param xmlids: the external ids of the records whose entries are read
        :return: ``{(model, field, xmlid): [(module, xmlid, English source, lang, translation)]}``,
            over every entry of the record; the translation is empty when the catalog leaves it out
        """
        entries = defaultdict(list)
        xmlids = set(xmlids)
        for module_name in sorted(module_names):
            for lang in langs:
                for path in get_po_paths(module_name, lang):
                    index = self._read_catalog(path)
                    for xmlid in index.keys() & xmlids:
                        for key, source, value in index[xmlid]:
                            entries[key].append((module_name, xmlid, source, lang, value))
        return entries

    @api.model
    def _read_catalog(self, path):
        """Return the entries a catalog file gives records, by external id.

        :param str path: a PO file, read with the template of its module, or a template
        :return: ``{xmlid: ((model, field, xmlid), English source, translation), ...}``; the
            translation is empty when the file leaves it out
        """
        stat = os.stat(path)
        return _parse_catalog(path, stat.st_mtime_ns, stat.st_size)

    @api.model
    def _get_branding_modules(self):
        """Return the names of the branding modules installed, or being installed or updated."""
        # sudo: a language install reads the module states whatever the access of the user who asks for it
        modules = self.sudo().search([
            ('name', '=like', 'viin_brand%'), ('state', 'in', ('installed', 'to install', 'to upgrade')),
        ])
        return sorted(name for name in modules.mapped('name') if _is_branding_module(name))

    @api.model
    def _get_branding_rewords(self, modules=()):
        """Return what each branding module re-words of the records of other modules.

        A branding module re-words a field of a record when its catalog template gives it an English
        text other than the one the template of a module owning the record gives it. What a branding
        module re-words is kept with the registry, and read again when the module is among
        ``modules``, whose loading may give its records new external ids.

        :param modules: the names of the modules being loaded
        :return: ``{branding module: (texts, records)}``: ``texts`` is ``{(model, field): {English}}``
            of the plain fields it re-words, ``records`` is ``{(model, field): {xmlid}}`` of the
            records whose field translated term by term its catalog names
        """
        # kept with the registry: the loader commits after each module, which empties the cursor cache
        cache = vars(self.env.registry).setdefault('viin_brand_rewords', {})
        branding_modules = self._get_branding_modules()
        for module_name in set(cache) - set(branding_modules):
            del cache[module_name]
        unread = [name for name in branding_modules if name not in cache or name in modules]
        named = {}
        for module_name in unread:
            named[module_name] = defaultdict(dict)
            pot_path = _get_pot_path(module_name)
            for xmlid, rows in self._read_catalog(pot_path).items() if pot_path else ():
                for (model, field_name, _xmlid), source, _value in rows:
                    field = model in self.env and self.env[model]._fields.get(field_name)
                    if field and field.translate and field.store:
                        named[module_name][xmlid][model, field_name] = source
        xmlids = set().union(*named.values())
        aliases = self._get_record_xmlids(xmlids) if xmlids else {}
        for module_name, sources_by_xmlid in named.items():
            texts, records = defaultdict(set), defaultdict(set)
            for xmlid, sources in sources_by_xmlid.items():
                owners = [
                    alias for alias in aliases.get(xmlid, ()) if not _is_branding_module(alias.split('.', 1)[0])
                ]
                for (model, field_name), english in sources.items():
                    if callable(self.env[model]._fields[field_name].translate):
                        if owners:
                            records[model, field_name].add(xmlid)
                    elif any(source != english for source in self._read_template_sources(owners, model, field_name)):
                        texts[model, field_name].add(english)
            cache[module_name] = (texts, records)
        return {name: cache[name] for name in branding_modules}

    @api.model
    def _read_template_sources(self, xmlids, model, field_name):
        """Return the English texts the templates of the modules of ``xmlids`` give a field of them."""
        sources = set()
        for xmlid in xmlids:
            pot_path = _get_pot_path(xmlid.split('.', 1)[0])
            rows = self._read_catalog(pot_path).get(xmlid, ()) if pot_path else ()
            sources.update(source for (row_model, row_field, _xmlid), source, _value in rows if (
                (row_model, row_field) == (model, field_name)
            ))
        return sources

    @api.model
    def _get_branding_english_targets(self, modules, rewords):
        """Return the records whose translations the loading of ``modules`` may have left stale.

        They are the records of ``modules`` that hold an English text a branding module re-words,
        and, for a branding module of ``modules``, every record that holds an English text it
        re-words (an inherited field takes the help of the field it re-words) and the records
        its catalog names term by term.

        :param rewords: the result of :meth:`_get_branding_rewords`
        :return: ``[(records, field name)]``
        """
        texts, own_texts, term_records = defaultdict(set), defaultdict(set), defaultdict(set)
        for module_name, (module_texts, module_records) in rewords.items():
            for key, english in module_texts.items():
                texts[key] |= english
                if module_name in modules:
                    own_texts[key] |= english
            if module_name in modules:
                for key, xmlids in module_records.items():
                    term_records[key] |= xmlids
        self.env['ir.model.data'].flush_model()
        targets = []
        for (model, field_name), english in texts.items():
            records = self.env[model]
            records.flush_model([field_name])
            ids = {record_id for [record_id] in self.env.execute_query(SQL(
                """SELECT m.id FROM ir_model_data imd JOIN %s m ON m.id = imd.res_id
                   WHERE imd.model = %s AND imd.module = ANY(%s) AND m.%s->>'en_US' = ANY(%s)""",
                SQL.identifier(records._table), model, list(modules), SQL.identifier(field_name), list(english),
            ))}
            if own_texts.get((model, field_name)):
                ids.update(record_id for [record_id] in self.env.execute_query(SQL(
                    "SELECT id FROM %s WHERE %s->>'en_US' = ANY(%s)",
                    SQL.identifier(records._table), SQL.identifier(field_name), list(own_texts[model, field_name]),
                )))
            targets.append((records.browse(sorted(ids)), field_name))
        for (model, field_name), xmlids in term_records.items():
            records = self.env[model]
            for xmlid in xmlids:
                records |= self.env.ref(xmlid, raise_if_not_found=False) or records
            targets.append((records, field_name))
        return [(records, field_name) for records, field_name in targets if records]

    @api.model
    def _read_branding_translations(self, branding_modules, langs):
        """Return the translations the catalogs of the branding modules give English texts.

        Within a module, the catalog of a regional language (``de_CH``) wins over the one of its base
        language (``de``), as the core loader applies them.

        :return: ``{(model, field, English, lang): {translation}}``
        """
        branding = defaultdict(set)
        for module_name in branding_modules:
            for lang in langs:
                values = {}
                for path in get_po_paths(module_name, lang):
                    for rows in self._read_catalog(path).values():
                        for (model, field_name, _xmlid), source, value in rows:
                            if value:
                                values[model, field_name, source, lang] = value
                for key, value in values.items():
                    branding[key].add(value)
        return branding

    @api.model
    def _apply_branding_english(self, modules, langs):
        """Give the records holding the English of a branding module its translation, else that English.

        The catalog of the module owning a record translates the English the record has without the
        branding, and the loader keeps that translation. A record whose field holds an English text a
        branding module re-words takes, in each language, the translation a branding catalog gives
        that text, else the translation a catalog of the record gives it, else the text itself. A
        field translated term by term is decided term by term.

        A translation is replaced only while it is the English of the record or a text the catalogs
        know (their English and their translations): a text a user wrote is kept. Running it again
        changes nothing.

        :param modules: the names of the modules whose catalogs were loaded; only the records they
            can have changed are decided (:meth:`_get_branding_english_targets`)
        :param langs: language codes
        """
        langs = [code for code in langs if code != 'en_US']
        if not langs:
            return
        rewords = self._get_branding_rewords(modules)
        targets = self._get_branding_english_targets(set(modules), rewords)
        if not targets:
            return
        aliases = defaultdict(set)
        for records, _field_name in targets:
            for res_id, xmlid in self.env.execute_query(SQL(
                "SELECT res_id, module || '.' || name FROM ir_model_data WHERE model = %s AND res_id = ANY(%s)",
                records._name, records.ids,
            )):
                aliases[records._name, res_id].add(xmlid)
        named = set().union(*aliases.values())
        entries = self._read_stock_texts({xmlid.split('.', 1)[0] for xmlid in named} | set(rewords), langs, named)
        branding = self._read_branding_translations(rewords, langs)
        selected = TranslationImporter(self.env.cr, verbose=False)
        for records, field_name in targets:
            # sudo: a catalog applies to the records whatever the rules that hide them from the user
            for record in records.sudo():
                names = aliases[record._name, record.id]
                if not names:
                    continue
                record_entries = [entry for name in names for entry in entries[record._name, field_name, name]]
                select = (
                    self._select_branding_terms if callable(record._fields[field_name].translate)
                    else self._select_branding_english
                )
                select(selected, record, field_name, min(names), langs, record_entries, branding)
        selected.save(force_overwrite=True)

    @api.model
    def _select_branding_english(self, selected, record, field_name, xmlid, langs, entries, branding):
        """Select the translations of a plain field that holds the English of a branding module.

        :param entries: the entries of the catalogs naming the record (:meth:`_read_stock_texts`)
        :param branding: ``{(model, field, English, lang): {translation}}`` of the branding catalogs
        """
        english = record.with_context(lang='en_US')[field_name]
        for lang in langs:
            stored = record.with_context(lang=lang)[field_name]
            translations, target = _translations_of(branding, entries, record._name, field_name, english, lang)
            if stored == target or stored in translations:
                continue
            if stored == english or stored in _catalog_texts(entries, lang):
                selected.model_translations[record._name][field_name][xmlid][lang] = target

    @api.model
    def _select_branding_terms(self, selected, record, field_name, xmlid, langs, entries, branding):
        """Select the term translations of a field that holds terms of a branding module.

        Each English term takes the translation :meth:`_select_branding_english` gives a plain text,
        and the whole value is replaced as :meth:`_select_terms` replaces it.
        """
        field = record._fields[field_name]
        english_terms = _terms_of(field, record.with_context(lang='en_US')[field_name])
        terms = defaultdict(dict)
        for lang in langs:
            stored_terms = _terms_of(field, record.with_context(lang=lang)[field_name])
            if len(stored_terms) != len(english_terms):
                stored_terms = [None] * len(english_terms)
            for term, stored in zip(english_terms, stored_terms):
                translations, target = _translations_of(branding, entries, record._name, field_name, term, lang)
                terms[term][lang] = stored if stored in translations else target
        if terms:
            self._select_terms(selected, record, field_name, xmlid, terms, entries)

    @api.model
    def _get_catalog_xmlids(self, importer):
        """Return the external ids of an importer's entries whose record exists."""
        xmlids = {
            xmlid
            for dictionary in (importer.model_translations, importer.model_terms_translations)
            for fields in dictionary.values()
            for records in fields.values()
            for xmlid in records
        }
        if not xmlids:
            return set()
        self.env['ir.model.data'].flush_model()
        self.env.cr.execute(
            "SELECT module || '.' || name FROM ir_model_data"
            " WHERE module || '.' || name IN %s AND res_id IS NOT NULL",
            [tuple(xmlids)],
        )
        return {xmlid for [xmlid] in self.env.cr.fetchall()}

    @api.model
    def _get_record_xmlids(self, xmlids):
        """Return, for each external id of ``xmlids``, every external id of its record, itself included."""
        self.env['ir.model.data'].flush_model()
        self.env.cr.execute(
            "SELECT named.module || '.' || named.name, alias.module || '.' || alias.name"
            " FROM ir_model_data named"
            " JOIN ir_model_data alias ON alias.model = named.model AND alias.res_id = named.res_id"
            " WHERE named.module || '.' || named.name IN %s",
            [tuple(xmlids)],
        )
        aliases = defaultdict(set)
        for xmlid, alias in self.env.cr.fetchall():
            aliases[xmlid].add(alias)
        return aliases

    @api.model
    def _get_catalog_record(self, xmlids, xmlid, model):
        """Return the record of an external id of ``xmlids``, an empty recordset when it is not a ``model``.

        The record is read as superuser: a language install runs as the user who asked
        for it, and a catalog applies to the records whatever the rules that hide them
        from that user, as the core importer writes them.
        """
        record = self.env.ref(xmlid, raise_if_not_found=False) if xmlid in xmlids else None
        if record is None or record._name != model:
            return self.env[model]
        return record.sudo()

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Leave the Enterprise flag out of every field list that offers fields by their label.

        The web client's filter, grouping and export pickers ask for all the fields with their
        ``string``; a view, or a caller that asks for named fields or for attributes without a
        label (the validation of a view asks for ``readonly`` and ``required``), still reads it, but
        as a field that cannot be grouped on, so the Custom Group picker, which lists the fields the
        views of the action load, does not offer it.
        """
        fields = super().fields_get(allfields=allfields, attributes=attributes)
        if not allfields and (attributes is None or 'string' in attributes):
            fields.pop('to_buy', None)
        if 'groupable' in fields.get('to_buy', ()):
            fields['to_buy']['groupable'] = False
        return fields

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        """Leave the categories that hold no module an Apps list shows out of the search panel."""
        result = super().search_panel_select_range(field_name, **kwargs)
        if field_name == 'category_id' and result.get('values'):
            shown = self.with_context(active_test=False)
            result['values'] = [
                value for value in result['values']
                if shown.search_count([('category_id', 'child_of', value['id']), ('to_buy', '=', False)])
            ]
        return result

    @api.model
    @api.ormcache()
    def _get_industry_categories_from_apps(self):
        """Never ask the apps store of Odoo for industry categories."""
        return []

    def _button_immediate_function(self, function):
        try:
            return super()._button_immediate_function(function)
        except UserError as error:
            raise debrand_exception(error)

    def button_immediate_install(self):
        self._check_iap_modules_are_not_requested()
        return super().button_immediate_install()

    def _check_iap_modules_are_not_requested(self):
        """Refuse an explicit request, from the user interface, to install an Odoo IAP module.

        Only the records the user asked for are checked: dependencies and auto-installed modules
        are resolved later inside ``button_install`` and are never refused. Installing or updating
        from the command line is not refused, and neither is a script, which has no HTTP request.
        """
        if not request or any(config.get(key) for key in ('init', 'update')):
            return
        refused = self.filtered(lambda module: module.name in IAP_MODULES and module.state == 'uninstalled')
        if refused:
            raise UserError(_(
                "The Odoo IAP modules cannot be installed from the user interface: %s",
                ', '.join(refused.mapped('shortdesc')),
            ))
