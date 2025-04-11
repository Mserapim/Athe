Ext._define('raf.autoreference.DetailWindow', {
    extend: 'Ext.Window',

    getAutoreferenceGrid: function(cfg) {
        if(!this._autoreferenceGrid) {
            this._autoreferenceGrid = Ext._create('raf.autoreference.Grid', {
                 region: 'center',
                 layout: 'fit',
                 border: false,
                 gridAutoLoad: false,
                 columnAction: false,
                 hideItemsToolbar:['add', 'edit', 'remove',],
                 doubleClickHandler: function(){},
            });
        }
        return this._autoreferenceGrid;
    },

    activity: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._activity = value;

            if(dispatch) this.observerActivity();
        }

        return this._activity;
    },

    observerActivity: function() {
        var value = this.activity();
        if(value) {
            this.getAutoreferenceGrid().setFilterProperty('activity', value, 100, true);
        }else {
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [

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

        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Relação de manifestações',
            width: 650,
            height: 500,
        });

        Ext.apply(cfg, {
            layout: 'border',
            modal: true,
            items: [
                this.getAutoreferenceGrid(cfg)
            ],
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        raf.autoreference.DetailWindow.superclass.constructor.call(this, cfg);

        this.activity(this.params.activity);
    }
});
