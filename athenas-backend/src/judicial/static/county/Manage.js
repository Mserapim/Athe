/**
 *
 **/
Ext._define('judicial.county.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getCountyGrid: function() {
        if(!this._countyGrid) {
            this._countyGrid = Ext._create('judicial.county.Grid', {
                region: 'center',
                minWidth: 500
            });

            this._countyGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.county(data.get('pk'));
                },
                rowdeselect: function() {
                    this.county(null);
                }
            });
        }

        return this._countyGrid;
    },

    getExecutionOrganGrid: function() {
        if(!this._executionOrganGrid) {
            this._executionOrganGrid = Ext._create('judicial.county.ExecutionOrganGrid', {
                region: 'east',
                gridAutoLoad: false,
                minWidth: 650,
                width: Ext.getBody().getBox().width * 0.5,
                split: true,
                allowAdd: false,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false
            });

            var tbar = this._executionOrganGrid.getToolbar();

            for(var i = 0; i < 4; i++)
                tbar.remove(0);
        }

        return this._executionOrganGrid;
    },

    county: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._county = value;

            !prevent && this.observeCounty();
        }

        return this._county;
    },

    observeCounty: function() {
        var value = this.county();

        if(value) {
            this.getExecutionOrganGrid().enable();
            this.getExecutionOrganGrid().setFilterProperty(
                'localidade__counties__id',
                value,
                1001
            );
        }
        else {
            this.getExecutionOrganGrid().disable();
            this.getExecutionOrganGrid().setFilterProperty(
                'localidade__counties__id',
                0,
                1001,
                false
            );
            this.getExecutionOrganGrid().getStore().removeAll();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Comarcas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getCountyGrid(),
                    this.getExecutionOrganGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        judicial.county.Manage.superclass.constructor.call(this, cfg);
        this.county(null);
    }
});
