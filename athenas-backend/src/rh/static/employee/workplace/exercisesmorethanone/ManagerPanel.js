/**
 *
 **/

Ext._define('rh.employee.workplace.exercisesmorethanone.ManagerPanel', {
    extend: 'Ext.Panel',

    __title: 'Locais mais de 1 exercício',

    getWorkplaceGrid: function(cfg_window, cfg) {
        if(!this._workplaceGrid){
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    title: 'Locais de Lotação',
                    region: 'center',
                    border: false,
                    split: true,
                    minHeight: 150,
                    height: 200,
                    columnAction: false,
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download'],
                    hideActions: ['edit', ],
                    hideItemsToolbar: ['add', 'edit', 'remove'],
                    doubleClickHandler: function(){}
                }
            );
            this._workplaceGrid = Ext._create('rh.workplace.MoreThanOneGrid', cfg);

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
            grid = this.getEmployeeWorkassignmentGrid();
            grid.setFilterProperty('lotacao', value, 6)
            grid.enable();
        }
        else {
            grid = this.getEmployeeWorkassignmentGrid();
            grid.disable();
            grid.setFilterProperty('lotacao', 0, 6, false);
            grid.getStore().removeAll();
        }
    },

    getEmployeeWorkassignmentGrid: function(cfg_window, cfg) {
        if(!this._employeeWorkassignmentGrid) {
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                    {
                        title: 'Exercícios',
                        region: 'south',
                        split: true,
                        minHeight: 200,
                        height: 450,
                        hideActions: ['edit', 'remove', 'copy'],
                        hideItemsToolbar: ['add', 'edit', 'remove'],
                        doubleClickHandler: function(){}
                    }
            );
            this._employeeWorkassignmentGrid = Ext._create('rh.employee.workplace.exercisesmorethanone.Grid', cfg);
        }
        return this._employeeWorkassignmentGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                region: 'center',
                layout: 'border',
                border: false,
                scope: this,
                items: [
                    this.getWorkplaceGrid(cfg, {departament: cfg.departament}),
                    this.getEmployeeWorkassignmentGrid(cfg, {departament: cfg.departament}),
                ],
            }
        );
        rh.employee.workplace.exercisesmorethanone.ManagerPanel.superclass.constructor.call(this, cfg);
    }
});
