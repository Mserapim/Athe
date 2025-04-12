
Ext._define('raf.management.ManagementRAF', {
    extend: 'Ext.Window',

    getManagementGroupGrid: function() {
        if(!this._managementGroupGrid) {
            this._managementGroupGrid = Ext._create('raf.management.GroupGrid', {
                region: 'west',
                title: 'RAFs',
                width: 450,
                maxWidth: 450,
                minWidth: 250,
                split: true,
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                hideHeaders: true
            });
            this._managementGroupGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.rafAction(selection[0]);
                    else
                        this.rafAction(null);
                }
            });
        }
        return this._managementGroupGrid;
    },

    rafAction: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._rafAction = value;
            if(dispatch)
                this.observeRafAction();
        }
        return this._rafAction;
    },

    observeRafAction: function() {
        var value = this.rafAction();
        if(value) {
            this.getRAFGrid().enable();
            this.getRAFGrid().setParam('month', value.get('month'));
            this.getRAFGrid().setParam('year', value.get('year'));
            this.getRAFGrid().setFilterProperty('month', value.get('month'), 0, false);
            this.getRAFGrid().setFilterProperty('year', value.get('year'), 1);
        } else  {
            this.getRAFGrid().disable();
            this.getRAFGrid().getStore().removeAll();
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];
        return this._buttons;
    },

    getRAFGrid: function(cfg) {
        if(!this._rafGrid) {
            this._rafGrid = Ext._create('raf.functionalactivityreport.Grid', {
                title: 'Membros/Status',
                region: 'center',
                split: true,
                border: false,
                columnAction: false,
                gridAutoLoad: false,
                allowRemove: false,
                disabled: false,
                hideColumns: ['year','month'],
                hideItemsToolbar: ['add', 'edit', 'remove', '-', 'download'],
                doubleClickHandler: function(){},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                managementGroupGrid: this.getManagementGroupGrid(cfg),
            });
        }
        return this._rafGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerencimento RAF',
                modal: true,
                width: Ext.getBody().getBox().width * 0.7,
                height: Ext.getBody().getBox().height * 0.85
            }
        );

        Ext.apply(
          cfg,
          {
              layout: 'border',
              border: false,
              buttons: this.getButtons(),
              items: [
                this.getManagementGroupGrid(cfg),
                this.getRAFGrid(cfg),
              ]
          }
        );
        raf.management.ManagementRAF.superclass.constructor.call(this, cfg);
    }
});
