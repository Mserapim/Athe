
Ext._define('judicial.parts.GrantConfidentialAccessWindowAdmin', {
    extend: 'judicial.parts.ConfidentialAccessWindow',
    rest: 'judicial.parts.GrantConfidentialAccessRestful',

    width: '90%',

    getAccessPersonGrid: function(cfg) {
        if(!this._accessPersonGrid) {
            this._accessPersonGrid = Ext._create('judicial.parts.PersonHasAccessGrid', {
                title: 'Pessoas Autorizadas',
                gridAutoLoad: false,
                configOrderToolBar: [],
                columnAction: false,
                doubleClickHandler: function() {},
            });
        }
        return this._accessPersonGrid;
    },

    getPersonAccessTab: function(cfg){
        if(!this._personAccessTab)
            this._personAccessTab = Ext._create('Ext.Panel',{
                layout: 'form',
                title: 'Pessoas autorizadas',
                border: false,
                frame: false,
                height: 520,
                flex: 1.0,
                layout: {
                    type:'hbox',
                    align: 'stretch'
                },
                items: [
                    this.getPartLawsuitAccessGrid(cfg),
                    this.getAccessPersonGrid(cfg)
                ]
            });
        return this._personAccessTab;
    },

    observerPartAccess: function() {
        var value = this.partAccess();

        if(value) {
            this.getAccessPersonGrid().enable();
            this.getAccessPersonGrid().setParam('access', value);
            this.getAccessPersonGrid().setFilterProperty('access', value, 1000);
        } else {
            this.getAccessPersonGrid().disable();
            this.getAccessPersonGrid().setParam('access', value);
            this.getAccessPersonGrid().setFilterProperty('access', 0, 1000, false);
            this.getAccessPersonGrid().getStore().removeAll({});
        }
    },

    partAccess: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._partAccess = value;

            if(dispatch) this.observerPartAccess();
        }

        return this._partAccess;
    },

    getPartLawsuitAccessGrid: function(cfg) {
        if(!this._partlawsuitAccessGrid) {
            this._partlawsuitAccessGrid = Ext._create('judicial.parts.PartLawsuitAccessGrid', {
                title: 'Documento com Sigilo',
                flex: 1.0,
                minWidth: 400,
                doubleClickHandler: function() {},
                gridAutoLoad: false,
                configOrderToolBar: [],
                columnAction: false,
            });

            this._partlawsuitAccessGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    if(selm.getSelections().length > 0)
                        this.partAccess(selm.getSelections()[0].get('pk'));
                    else
                        this.partAccess(null);
                }
            });
        }

        return this._partlawsuitAccessGrid;
    },


    getTabPanelItems: function(cfg){
        return this.getPersonAccessTab(cfg);
    },

    partlawsuit: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._partlawsuit = value;

            if(dispatch)
                this.observeParlawsuit();
        }

        return this._partlawsuit;
    },

    observeParlawsuit: function() {
        var value = this.partlawsuit();
        this.getPartLawsuitAccessGrid().setFilterProperty('lawsuit', value, 10001, false);

        if(value)
            this.getPartLawsuitAccessGrid().getStore().load();
        else
            this.getPartLawsuitAccessGrid().getStore().removeAll();
    },

    getButtons: function(cfg) {
        return [];
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {
            title: 'Visualizar Permissões'
        });

        judicial.parts.GrantConfidentialAccessWindowAdmin.superclass.constructor.call(this, cfg);
        this.on({
            scope: this,
            render: function() {
                this.partlawsuit(this.lawsuit.id || null);
            }
        });
        this.observerPartAccess();
    }
});
