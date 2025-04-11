
Ext._define('common.official_journal.filters.FilterWindow', {
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
                                values[p.property],
                                p.stage,
                                false
                            );
                        }
                    );
                else {
                    let value = '';
                    if(p.property.startsWith('send_date')){
                        let lista = values[p.property].split('/');
                        value = ''.concat(lista[2], '-', lista[1], '-', lista[0]);
                        // console.log(value);
                    }else{
                        value = values[p.property];
                    }

                    me.grid.setFilterProperty(
                        p.property,
                        value,
                        p.stage,
                        false
                    );

                }
            }
        );

        this.grid.getStore().load();
        this.close();
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

        common.official_journal.filters.FilterWindow.superclass.constructor.call(this, cfg);

    }
});
