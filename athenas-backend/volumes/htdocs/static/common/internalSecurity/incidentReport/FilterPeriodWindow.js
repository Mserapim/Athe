/**
 *
 **/

Ext._define('common.internalSecurity.incidentReport.FilterPeriodWindow', {
    extend: 'common.internalSecurity.incidentReport.FilterBaseWindow',

    width: 450,

    properties: [
        {stage: 1004, property: 'reported_at__gte', suffix: ' 00:00:00' },
        {stage: 1005, property: 'reported_at__lte', suffix: ' 23:59:59' }
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 120,
                items: [
                    {
                        xtype: 'compositefield',
                        fieldLabel: 'Período',
                        items: [
                            {
                                xtype: 'datefield',
                                name : 'reported_at__gte',
                                allowBlank: false,
                                format: 'd/m/Y'
                            },
                            {
                                xtype: 'displayfield',
                                value: ' até '
                            },
                            {
                                xtype: 'datefield',
                                name : 'reported_at__lte',
                                allowBlank: false,
                                format: 'd/m/Y'
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    readFilters: function() {
        var filters = this.grid.getFilter();
        var properties = this.properties.map(
            function(directive) {
                return [directive.property, directive.propertyAliases];
            }
        );
        var values = {};

        properties.forEach(
            function(item) {
                var property, propertyAliases;

                property = item[0];
                propertyAliases = item[1] || [];

                if(Object.keys(values).indexOf(property) < 0){
                    filters.forEach(
                        function(directive) {
                            console.log(directive);
                            if(propertyAliases.indexOf(directive.property) >= 0 || property === directive.property){
                                values[property] = directive.value.split(' ')[0];
                            }
                        }
                    );
                }
            }
        );

        this.getFormPanel().getForm().setValues(values);
    },

    applyFilter: function() {
        var values = this.getFormPanel().getForm().getValues();
        var me = this;

        this.properties.forEach(
            function(p) {
                if(p.propertyAliases)
                    p.propertyAliases.forEach(
                        function(alias) {
                            me.grid.setFilterProperty(
                                alias,
                                Ext.util.Format.date(
                                    Date.parseDate(
                                        values[p.property] + p.suffix,
                                        'd/m/Y H:i:s'
                                    ),
                                    'Y-m-d H:i:s'
                                ),
                                p.stage,
                                false
                            );
                        }
                    );
                else{
                    me.grid.setFilterProperty(
                        p.property,
                        Ext.util.Format.date(
                            Date.parseDate(
                                values[p.property] + p.suffix,
                                'd/m/Y H:i:s'
                            ),
                            'Y-m-d H:i:s'
                        ),
                        p.stage,
                        false
                    );
                }
            }
        );

        this.grid.getStore().load();
        this.close();
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {
                title: 'Filtrar por Período'
            }
        );

        common.internalSecurity.incidentReport.FilterPeriodWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
