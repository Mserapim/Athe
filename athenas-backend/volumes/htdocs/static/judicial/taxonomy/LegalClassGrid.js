
Ext._define('judicial.taxonomy.LegalClassGrid', {
    extend: 'judicial.taxonomy.LegalClassificationGrid',

    restWindow: 'judicial.taxonomy.LegalClassWindow'
});

core.RestfulGrid.register(
    'judicial.taxonomy.LegalClassRestful',
    'judicial.taxonomy.LegalClassGrid'
);
