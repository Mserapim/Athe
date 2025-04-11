
Ext._define('rh.replacement.WorkplaceReplacementManager', {
    extend: 'toolkit.widget.TabPanel',

    getWorkplaceGrid: function() {
        if(!this._workplaceGrid){
            this._workplaceGrid = Ext._create('rh.workplace.Grid', {
                region: 'center',
                border: false,
                split: true,
                minHeight: 250,
                columnAction: false,
                hideActions: ['remove', 'copy', 'edit'],
                hideItemsToolbar: ['add', 'remove', 'edit', 'migrar'],
                doubleClickHandler: function(){},
            });

            this._workplaceGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.workplace(record.get('pk'));
                },
                rowdeselect: function(sm) {
                    this.workplace(null);
                }
            });

            this._workplaceGrid.getStore().on({
                scope: this,
                load: function() {
                    this.workplace(null);
                }
            });

            this._workplaceGrid.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._workplaceGrid.getSelectionModel().getSelected());

                    if(selected)
                        this.workplace(selected.get('pk'));
                    else
                        this.workplace(null);
                }
            });
        }

        return this._workplaceGrid;
    },

    workplace: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._workplace = value;

            !prevent && this.observeWorkplace();
        }

        return this._workplace;
    },

    observeWorkplace: function() {
        var value = this.workplace();
        var grid;

        if(value) {
            grid = this.getReplacementGrid();
            grid.setParam('replaced', value);
            grid.setFilterProperty('replaced', value, 1001);
            grid.enable();
        }
        else {
            grid = this.getReplacementGrid();
            grid.setParam('replaced', 0);
            grid.setFilterProperty('replaced', 0, 1001, false);
            grid.getStore().removeAll();
            grid.disable();
        }
    },

    getReplacementGrid: function(args) {
        if(!this._replacement)
            this._replacement = Ext._create('rh.replacement.Grid', {
                department: args.department,
                region: 'south',
                border: false,
                gridAutoLoad: false,
                minHeight: 300,
                height: 350,
            });
        return this._replacement;
    },

    getPanelAction: function(args) {
        if(!this._panelAction)
            this._panelAction = Ext._create('Ext.Panel', {
                region: 'north',
                frame: true,
                border: false,
                height: 40,
                align: 'center',
                items:[
                    this.getActionButton(),
                ]
            });
        return this._panelAction;
    },

    getActionButton: function(){
        if(!this._actionButton){
            this._actionButton = Ext._create('Ext.Button', {
                text: '<p style="font-size:10px; text-align:center; font-weight: bold;">Atualizar publicação em todos</p>',
                handler: function(){
                    var wnd = Ext._create('rh.replacement.WindowUpdateDocument', {});
                    wnd.show();
                }
            });
        }
        return this._actionButton;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Tabela - Substituições Automáticas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getPanelAction(),
                    this.getWorkplaceGrid(),
                    this.getReplacementGrid({department: cfg.department}),
                ]
            }
        );

        rh.replacement.WorkplaceReplacementManager.superclass.constructor.call(this, cfg);
    }
});
