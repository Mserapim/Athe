Ext._define('esocial.manager.PeriodFilterAction', {
    extend: 'core.fields.ComboField',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                // xtype: 'rest-autocompletefield',
                fieldLabel: 'Selecione o Período',
                name: 'period',
                rest: 'rh.gfp.payroll.PeriodRestful',
                propertyName: 'period',
                hiddenName: 'period',
                valueField: 'pk',
                emptyText: 'Informe o Período para filtrar',
                triggerAction: 'all',
                lazyRender: true,
                lazyInit: true,
                displayField: 'unicode',
                width: 200,
            }
        );

        esocial.manager.PeriodFilterAction.superclass.constructor.call(this, cfg);

        var store = this.getStore();
        var all_groups = new Ext.data.Record({
            pk: 0,
            unicode: 'TODOS OS PERÍODOS',
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
                    if (record.data.pk === 0){
                        objToFilter.removeFilterProperty("competence_month", 800, false);
                        objToFilter.removeFilterProperty("competence_year", 900);
                    }else{
                        objToFilter.setFilterProperty("competence_month", record.data.mes, 800, false);
                        objToFilter.setFilterProperty("competence_year", record.data.ano, 900);
                    }
                }
            }
        });
    }
});
