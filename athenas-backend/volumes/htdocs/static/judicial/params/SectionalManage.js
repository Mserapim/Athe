/**
 *
 **/
Ext._define('judicial.params.SectionalManage', {
    extend: 'toolkit.widget.TabPanel',

    getCountyGrid: function() {
        if(!this._countyGrid) {
            this._countyGrid = Ext._create('judicial.county.Grid', {
                region: 'west',
                minWidth: 400,
                width: 400,
                split: true,
                columnAction: false,
                doubleClickHandler: function() {},
                hideItemsToolbar: ['add', 'edit', 'remove', '-','download'],
            });

            this._countyGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var selection = selm.getSelections();

                    if(selection.length > 0)
                        this.county(selection[0].get('pk'));
                    else
                        this.county(null);
                }
            });
        }

        return this._countyGrid;
    },

    county: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._county = value;

            if(!prevent) this.observeCounty();
        }

        return this._county;
    },

    observeCounty: function() {
        var value = this.county();

        if(value) {
            this.getSectionalGrid().enable();
            this.getSectionalGrid().setParam('county', value);
            this.getSectionalGrid().setFilterProperty('county', value, 100);
        }
        else {
            this.getSectionalGrid().disable();
            this.getSectionalGrid().setParam('county', 0);
            this.getSectionalGrid().setFilterProperty('county', 0, 100, false);
            this.getSectionalGrid().getStore().removeAll();
        }
    },

    getSectionalGrid: function() {
        if(!this._sectionalGrid)
            this._sectionalGrid = Ext._create('judicial.params.SectionalGrid', {
                region: 'center',
                minWidth: 300,
                gridAutoLoad: false
            });

        return this._sectionalGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Regionais'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getCountyGrid(),
                    this.getSectionalGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        judicial.params.SectionalManage.superclass.constructor.call(this, cfg);
        this.observeCounty();
    }
});
