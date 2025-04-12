/**
 *
 **/
Ext._define('rh.administrativeunit.config.ManageConfiguration', {
    extend: 'Ext.Panel',

    getUnitConfig: function(cfg) {
        if(!this.config) {
            this.config = Ext._create('rh.administrativeunit.config.Grid', {
                title: 'do Órgão Público',
                anchor: '-1 30%',
                border: false,
                hideItemsToolbar: ['edit', 'remove', 'download'],
                collapsible: true,
            });
        }

        return this.config;
    },

    getEstablishmentConfig: function(cfg) {
        if(!this.estconfig) {
            this.estconfig = Ext._create('rh.administrativeunit.config.establishment.Grid', {
                title: 'da Unidade de órgão público',
                border: false,
                anchor: '-1 30%',
                hideItemsToolbar: ['edit', 'remove', 'download'],
                collapsible: true,
            });
        }

        return this.estconfig;
    },

    getTaxAllocationConfig: function(cfg) {
        if(!this.taxconfig) {
            this.taxconfig = Ext._create('rh.administrativeunit.config.taxallocation.Grid', {
                title: 'da Lotação tributária',
                border: false,
                hideItemsToolbar: ['edit', 'remove', 'download'],
                collapsible: true,
                anchor: '-1 31%',
            });
        }

        return this.taxconfig;
    },

    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Configurações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    {
                        xtype: 'panel',
                        region: 'center',
                        layout: 'anchor',
                        border: false,
                        items: [
                            this.getUnitConfig(cfg),
                            this.getEstablishmentConfig(cfg),
                            this.getTaxAllocationConfig(cfg),
                        ],
                    },
                ]
            }
        );

        rh.administrativeunit.config.ManageConfiguration.superclass.constructor.call(this, cfg);
    }
});
