
Ext._define('edocs.protocolo.filters.FilterWindow', {
    extend: 'Ext.Window',

    width: 450,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                ]
            });

        return this._formPanel;
    },

    clearFilter: function() {
        var me = this;

        var filter = this.grid.getFilter().filter(function(item) {
            if(!me.__itemInFilterProperties(item))
                return item;
        });

        this.grid.setFilter(filter);
        this.close();
    },

    __itemInFilterProperties: function(item) {
        return this.filterProperties.some(
            function(el) {
                return (el && el.property == item.property && el.stage == item.stage);
            }
        );
    },

    acceptFilter: function(value) {
        return (value !== undefined && value !== '');
    },

    prepareFilterValue: function(property, value) {
        return value;
    },

    applyFilter: function() {
        var values, filter, me;

        if(this.getFormPanel().getForm().isValid()) {
            values = this.getFormPanel().getForm().getValues();
            me = this;

            this.filterProperties.forEach(
                function(item) {
                    if(me.acceptFilter(values[item.property]))
                        me.grid.setFilterProperty(
                            item.property,
                            me.prepareFilterValue(item.property, values[item.property]),
                            item.stage,
                            false
                        );
                }
            );

            this.grid.getStore().reload();
            this.close();
        }
    },

    propertyStage: function(property) {
        var stage = false;

        this.filterProperties.every(
            function(item) {
                if(property == item.property) {
                    stage = item.stage;
                    return false;
                }
                else {
                    return true;
                }
            }
        );

        return stage;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Filtro'
            }
        );

        Ext.apply(
            cfg,
            {
                modal: true,
                border: false,
                items: [
                    this.getFormPanel()
                ],
                buttons: [
                    {
                        text: 'Limpar filtro',
                        scope: this,
                        handler: this.clearFilter
                    },
                    {
                        text: 'Filtrar',
                        scope: this,
                        handler: this.applyFilter
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: function() { this.close(); }
                    }
                ]
            }
        );

        edocs.protocolo.filters.FilterWindow.superclass.constructor.call(this, cfg);

        var values = {};
        var me = this;

        this.grid.getFilter().forEach(
            function(item) {
                if(me.__itemInFilterProperties(item))
                    values[item.property] = item.value.split(' ')[0];
            }
        );

        this.getFormPanel().getForm().setValues(values);
    }
});
