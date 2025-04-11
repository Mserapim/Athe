/**
 *
 **/
 Ext._define('rh.employee.workplace.managerbyworkplace.pendingexercises.ManagePanel', {
    extend: 'rh.employee.workplace.managerbyworkplace.ManagePanel',

    __title: 'Órgãos com exercícios pendentes',

    getWorkplaceGrid: function(cfg_window, cfg) {
        if(!this._workplaceGrid){
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    title: 'Locais de Lotação',
                    region: 'north',
                    split: true,
                    minHeight: 450,
                    height: 450,
                    columnAction: false,
                    gridAutoLoad: true,
                    hideActions: ['edit', 'remove', 'copy'],
                    hideItemsToolbar: ['add', 'edit', 'remove'],
                    doubleClickHandler: function(){}
                }
            );
            this._workplaceGrid = Ext._create('rh.workplace.PendingExercisesGrid', cfg);

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

            this._workplaceGrid.getStore().on({
                scope: this,
                load: function(store, records, opts) {
                    if(store.getTotalCount() > 0){
                        this.setTitle(this.__title + ' (' + store.getTotalCount() + ')');
                        this.ownerCt.setTitle(this.__title + ' (' + store.getTotalCount() + ')');
                    }else{
                        this.setTitle(this.__title);
                        this.ownerCt.setTitle(this.__title);
                    }
                }
            });
        }

        return this._workplaceGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            boder: false
        });
        rh.employee.workplace.managerbyworkplace.pendingexercises.ManagePanel.superclass.constructor.call(this, cfg);
    }
});
