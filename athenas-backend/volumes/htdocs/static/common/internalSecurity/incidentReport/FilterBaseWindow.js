/**
 *
 **/
Ext._define('common.internalSecurity.incidentReport.FilterBaseWindow', {
    extend: 'Ext.Window',

    width: 450,

    properties: [],

    clearFilter: function() {
        var grid = this.grid;

        this.properties.forEach(
            function(directive) {
                if(directive.propertyAliases)
                    directive.propertyAliases.forEach(
                        function(alias) {
                            grid.removeFilterProperty(alias, directive.stage, false);
                        }
                    );
                else
                    grid.removeFilterProperty(directive.property, directive.stage, false);
            }
        );

        grid.getStore().load();
        this.close();
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

                if(Object.keys(values).indexOf(property) < 0)
                    filters.forEach(
                        function(directive) {
                            if(propertyAliases.indexOf(directive.property) >= 0 || property === directive.property)
                                values[property] = directive.value;
                        }
                    );
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
                                values[p.property],
                                p.stage,
                                false
                            );
                        }
                    );
                else
                    me.grid.setFilterProperty(
                        p.property,
                        values[p.property],
                        p.stage,
                        false
                    );
            }
        );

        this.grid.getStore().load();
        this.close();
    },

    getFormPanel: function(cfg) {
        throw 'O metodo getFormPanel deve ser implementado, este é abstrato';
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Limpar',
                    scope: this,
                    handler: this.clearFilter
                },
                '->',
                {
                    text: 'Aplicar',
                    scope: this,
                    handler: this.applyFilter
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {
                title: 'Filter Base Window',
                buttonAlign: 'left'
            }
        );

        Ext.apply(
            cfg,
            {
                buttons: this.getButtons(cfg),
                items: [
                    this.getFormPanel(cfg)
                ]
            }
        );

        common.internalSecurity.incidentReport.FilterBaseWindow.superclass.constructor.call(this, cfg);
    }
});
