
Ext._define('judicial.parts.GrantConfidentialAccessWindow', {
    extend: 'judicial.parts.ConfidentialAccessWindow',

    rest: 'judicial.parts.GrantConfidentialAccessRestful',

    width: 1000,

    autoCreate: true,
    autoClose: false,

    renderAfterSign: function() {
        judicial.parts.GrantConfidentialAccessWindow.superclass.renderAfterSign.call(this);
        this.observerPartAccess();
        this.getPersonAccessTab().enable();
        this.getTabPanel().activate(this.getPersonAccessTab().getItemId());
        this.getMainPanel().disable();
    },

    getAccessPersonGrid: function(cfg) {
        if(!this._accessPersonGrid) {
            this._accessPersonGrid = Ext._create('judicial.parts.PersonHasAccessGrid', {
                title: 'Pessoas Autorizadas',
                minWidth: 345,
                gridAutoLoad: false,
                columnAction: false,
                disabled: false,
            });
        }
        return this._accessPersonGrid;
    },

    getPersonAccessTab: function(cfg){
        if(!this._personAccessTab)
            this._personAccessTab = Ext._create('Ext.Panel',{
                layout: 'form',
                disabled: true,
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

    getPartLawsuitAccessGrid: function(cfg) {
        if(!this._partlawsuitAccessGrid) {
            this._partlawsuitAccessGrid = Ext._create('judicial.parts.PartLawsuitAccessGrid', {
                title: 'Documento com Sigilo',
                toolbarHideLabel: true,
                flex: 1.0,
                minWidth: 245,
                doubleClickHandler: function() {},
                border: false,
                frame: false,
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

    getTabPanelItems: function(cfg){
        return judicial.parts.GrantConfidentialAccessWindow.superclass.getTabPanelItems.call(this, cfg).concat(this.getPersonAccessTab(cfg));
    },

    observer: function() {
        var instance = this.confidential();
        var selection = this.selection();
        var clear = false;

        if(selection == 2) {
            this.getControlPanel().enable();
            this.getPartLawsuitGrid().enable();
            this.getPartLawsuitSelectedGrid().enable();
            clear = false;
        } else {
            this.getControlPanel().disable();
            this.getPartLawsuitGrid().disable();
            this.getPartLawsuitSelectedGrid().disable();

            clear = true;
        }

        if(instance) {
            this.getPartLawsuitGrid().setFilterProperty('access_controls__in_grantconfidentialaccess', instance, -1000, !clear);
            this.getPartLawsuitSelectedGrid().setFilterProperty('access_controls__in_grantconfidentialaccess', instance, 1000, !clear);

            this.getPartLawsuitAccessGrid().setFilterProperty('in_grantconfidentialaccess', instance, 1000);

            if(clear){
                this.getPartLawsuitGrid().getStore().removeAll({});
                this.getPartLawsuitSelectedGrid().getStore().removeAll({});
            }

        } else {
            this.getPartLawsuitAccessGrid().setFilterProperty('in_grantconfidentialaccess', 0, 1000, false);

            this.getPartLawsuitGrid().setFilterProperty('access_controls__in_grantconfidentialaccess', 0, -1000, false);
            this.getPartLawsuitSelectedGrid().setFilterProperty('access_controls__in_grantconfidentialaccess', 0, 1000, false);

            this.getPartLawsuitAccessGrid().getStore().removeAll({});
            this.getPartLawsuitGrid().getStore().removeAll({});
            this.getPartLawsuitSelectedGrid().getStore().removeAll({});
        }

    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(cfg, {
            title: 'Decretar Sigilo'
        });

        judicial.parts.GrantConfidentialAccessWindow.superclass.constructor.call(this, cfg);

        this.observerPartAccess();
    }

});

judicial.PartLawsuitGrid.register('judicial.grantconfidentialaccess', 'judicial.parts.GrantConfidentialAccessWindow');
