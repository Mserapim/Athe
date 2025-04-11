Ext._define('rh.dayoff.acquisitionperiod.TypeOfFilterAction', {
    extend: 'core.fields.ComboField',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            propertyName: "group_period__configuration__type_of_usufruct",
            rest: "standard.ChoiceRestful",
            fieldLabel: "Tipo",
            hiddenName: "type_of_usufruct",
            valueField: "value",
            emptyText: "Informe Tipo para filtrar",
            triggerAction: "all",
            lazyRender: true,
            lazyInit: true,
            displayField: "unicode",
            width: 200,
            preFilter: [
                {
                    property: "name",
                    value: "CONFIGURATION_CHOICE",
                },
            ],
        });

        rh.dayoff.acquisitionperiod.TypeOfFilterAction.superclass.constructor.call(this, cfg);

        var store = this.getStore();
        var all_groups = new Ext.data.Record({
            pk: 0,
            unicode: 'TODOS OS TIPOS',
        });

        store.on('load', function () {
            store.insert(0, all_groups);
            store.commitChanges();
        });

        var objToFilter = this.objToFilter;

        this.on({
            scope: this,
            select: {
                buffer: 1,
                fn: function (combo, record, index) {
                    if (record.data.pk === 0)
                        objToFilter.removeFilterProperty(cfg.propertyName, 1010);
                    else
                        objToFilter.setFilterProperty(cfg.propertyName, record.data.value, 1010);
                }
            }
        });
    }
});
