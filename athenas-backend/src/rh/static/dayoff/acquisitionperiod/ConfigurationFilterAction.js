Ext._define('rh.dayoff.acquisitionperiod.ConfigurationFilterAction', {
    extend: 'core.fields.ComboField',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                propertyName: 'group_period__configuration',
                rest: 'rh.dayoff.configuration.Restful',
                fieldLabel: 'Configuração',
                hiddenName: 'configuration',
                valueField: 'pk',
                emptyText: 'Informe Configuração para filtrar',
                triggerAction: 'all',
                lazyRender: true,
                lazyInit: true,
                displayField: 'unicode',
                width: 200,
            }
        );

        rh.dayoff.acquisitionperiod.ConfigurationFilterAction.superclass.constructor.call(this, cfg);

        var store = this.getStore();
        var all_groups = new Ext.data.Record({
            pk: 0,
            unicode: 'TODAS AS CONFIGURAÇÕES',
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
                        objToFilter.removeFilterProperty(cfg.propertyName, 900);
                    else
                        objToFilter.setFilterProperty(cfg.propertyName, record.data.pk, 900);
                }
            }
        });
    }
});
