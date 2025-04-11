/**
 *
 **/
Ext._define('judicial.council.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getSessionGrid: function() {
        if(!this._sessionGrid) {
            this._sessionGrid = Ext._create('judicial.council.SessionGrid', {
                region: 'center',
                height: 200,
                maxHeight: 200,
            });

            this._sessionGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.observe(data.get('pk'));
                },
                rowdeselect: function() {
                    this.observe(null);
                }
            });

        }

        return this._sessionGrid;
    },

    getSessionItemGrid: function() {
        if(!this._sessionitemGrid) {
            this._sessionitemGrid = Ext._create('judicial.council.SessionItemGrid', {
                region: 'south',
                minHeight: 400,
                height: 600,
                disabled: true,
                gridAutoLoad: false,
            });

        }

        return this._sessionitemGrid;
    },

    observe: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._param = value;

            if(!prevent)
                this.observeSession();
        }

        return this._param;
    },

    observeSession: function(){

        var value = this.observe();

        if(value) {
            this.getSessionItemGrid().enable();
            this.getSessionItemGrid().setFilterProperty('session', value);
            this.getSessionItemGrid().setParam('session', value);
        }
        else {
            this.getSessionItemGrid().getStore().removeAll();
            this.getSessionItemGrid().disable();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Sessões'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getSessionGrid(),
                    this.getSessionItemGrid()
                ]
            }
        );

        judicial.council.Manage.superclass.constructor.call(this, cfg);
    }
});
