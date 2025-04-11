Ext._define('judicial.requestcollaboration.WindowManage', {
    extend: 'Ext.Window',

    width: 950,
    height: 650,

    getPersonGrid: function(cfg) {
        if(!this._personGrid) {
            this._personGrid = Ext._create('judicial.requestcollaboration.person.Grid', {
                title: 'Servidor',
                region: 'center',
                configOrderToolBar: ['addRequestCollaboration', 'inactivateCollaboration'],
                hideActions: ['remove', 'edit', 'copy'],
                allowRemove: false,
                allowUpdate: false,
                gridAutoLoad: false,
                hideColumns: ['unicode', 'origin_location_unicode', 'lawsuit_unicode'],
                flex: 1
            });

            this._personGrid.setParam('lawsuit', cfg.params.lawsuit);
            this._personGrid.setParam('origin_location', cfg.params.origin_location);
            this._personGrid.setFilterProperty('lawsuit', cfg.params.lawsuit, 100);
        }

        return this._personGrid;
    },

    getGeneralOrganGrid: function(cfg) {
        if(!this._generalOrganGrid) {
            this._generalOrganGrid = Ext._create('judicial.requestcollaboration.generalorgan.Grid', {
                title: 'Departamento',
                region: 'south',
                configOrderToolBar: ['addRequestCollaboration', 'inactivateCollaboration'],
                hideActions: ['remove', 'edit', 'copy'],
                allowRemove: false,
                allowUpdate: false,
                gridAutoLoad: false,
                hideColumns: ['unicode', 'origin_location_unicode', 'lawsuit_unicode'],
                flex: 1
            });

            this._generalOrganGrid.setParam('lawsuit', cfg.params.lawsuit);
            this._generalOrganGrid.setParam('origin_location', cfg.params.origin_location);
            this._generalOrganGrid.setFilterProperty('lawsuit', cfg.params.lawsuit, 100);
        }

        return this._generalOrganGrid;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        if (!cfg.params.lawsuit) {
            throw 'Não foi definido um Procedimento';
        }

        Ext.applyIf(cfg, {
           title: 'Gestor de Colaboração'
        });

        Ext.apply(cfg, {
            layout: {
                type:'vbox',
                align:'stretch'
            },
            items: [
                this.getPersonGrid(cfg),
                this.getGeneralOrganGrid(cfg),
            ]
        });

        judicial.requestcollaboration.WindowManage.superclass.constructor.call(this, cfg);
    }
});
