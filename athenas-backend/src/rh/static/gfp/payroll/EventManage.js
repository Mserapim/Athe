/**
 *
 **/

Ext._define('rh.gfp.payroll.EventManage', {
    extend: 'toolkit.widget.TabPanel',

    getEventGrid: function() {
        if(!this._eventGrid){
            this._eventGrid = Ext._create('rh.gfp.payroll.EventGrid', {
                region: 'center',
                ConfigEventGrid: this.getEventConfigGrid(),
            });
        }

        this._eventGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data){
                    this.config(data.get('pk'));
                },
                rowdeselect: function(){
                    this.config(null);
                },
        });

        return this._eventGrid;
    },

    getEventConfigGrid: function(){
        if(!this._configEventGrid){
            this._configEventGrid = Ext._create('rh.gfp.payroll.ConfigEventGrid', {
                region: 'south',
                // heigth: "50%",
                split: true,
                // allEvent: this,
                flex: 0.5,
                height: 400,
                split: true,
                gridAutoLoad: false
            });

        }

        return this._configEventGrid;
    },

    config: function(value, dispatch){
        dispatch = core.nullValue(dispatch, true)

        if(value !== undefined){
            this._config = value;

            if(dispatch) this.observeEvent();
        }
        else
            return this._config;
    },

    observeEvent: function(){
        if(this.config()){
            this.getEventConfigGrid().enable();
            this.getEventConfigGrid().setParam('event', this.config());
            this.getEventConfigGrid().setFilterProperty('event_id', this.config(), 100);
        }
        else{
            this.getEventConfigGrid().disable();
            this.getEventConfigGrid().getStore().removeAll();
            this.getEventConfigGrid().setFilterProperty('event_id', 0, 100, false);
        }
    },

    // getGrid: function() {
    //     if(!this._grid)
    //         this._grid = Ext._create('rh.gfp.payroll.EventGrid', {
    //             region: 'center'
    //         });

    //     return this._grid;
    // },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Eventos/Rubricas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:[
                    this.getEventGrid(),
                    this.getEventConfigGrid()
                ]
            }
        );

        rh.gfp.payroll.EventManage.superclass.constructor.call(this, cfg);
        this.observeEvent();

    }
});
