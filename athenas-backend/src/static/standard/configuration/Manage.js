/**
 *
 **/
Ext._define('standard.configuration.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getChoiceGrid: function(cfg) {
        if(!this._grid)
            this._grid = Ext._create('standard.configuration.Grid', {
                region: 'center'
            });

        this._grid.getSelectionModel().on({
            scope: this,
            rowselect: function(sm, index, data) {
                this.observe(data.get('pk'));
                this.getItemGrid().setParam('application',data.get('application'))
            },
            rowdeselect: function() {
                this.observe(null);
            }
        });

        return this._grid;
    },

    observe: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._param = value;

            if(!prevent)
                this.observeChoice();
        }

        return this._param;
    },

    observeChoice: function(){

        var value = this.observe();

        if(value) {
            this.getItemGrid().enable();
            this.getItemGrid().setParam('configuration', value);
            this.getItemGrid().setFilterProperty('configuration', value, 0);
        }
        else {
            this.getItemGrid().disable();
            this.getItemGrid().setParam('configuration', 0);
            this.getItemGrid().setFilterProperty('configuration', 0, 0, false);
            this.getItemGrid().getStore().removeAll();
        }
    },

    getItemGrid: function() {
        if(!this._subfaltaGrid) {
            this._subfaltaGrid = Ext._create('standard.configuration.item.Grid', {
                region: 'south',
                height: 400,
                disabled: true,
                gridAutoLoad: false,
            });

        }

        return this._subfaltaGrid;
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
                items: [
                    this.getChoiceGrid(),
                    this.getItemGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        standard.configuration.Manage.superclass.constructor.call(this, cfg);
    }
});
