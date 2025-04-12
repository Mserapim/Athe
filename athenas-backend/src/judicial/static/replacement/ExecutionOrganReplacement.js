
Ext._define('judicial.replacement.ExecutionOrganReplacement', {
    extend: 'toolkit.widget.TabPanel',

    getExecutionOrganGrid: function() {
        if(!this._executionOrganGrid){
            this._executionOrganGrid = Ext._create('judicial.county.ExecutionOrganGrid', {
                region: 'north',
                split: true,
                minHeight: 450,
                height: 450,
                columnAction: false,
                hideActions: ['remove', 'copy'],
                hideItemsToolbar: ['add', 'remove'],
            });

            this._executionOrganGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    this.executionOrgan(record.get('pk'));
                },
                rowdeselect: function(sm) {
                    this.executionOrgan(null);
                }
            });

            this._executionOrganGrid.getStore().on({
                scope: this,
                load: function() {
                    this.executionOrgan(null);
                }
            });

            this._executionOrganGrid.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._executionOrganGrid.getSelectionModel().getSelected());

                    if(selected)
                        this.executionOrgan(selected.get('pk'));
                    else
                        this.executionOrgan(null);
                }
            });
        }

        return this._executionOrganGrid;
    },

    executionOrgan: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._executionOrgan = value;

            !prevent && this.observeExecutionOrgan();
        }

        return this._executionOrgan;
    },

    observeExecutionOrgan: function() {
        var value = this.executionOrgan();
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
                region: 'center',
                gridAutoLoad: false,
                minHeight: 300
            });
        return this._replacement;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Tabela de Substituições Automáticas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getExecutionOrganGrid(),
                    this.getReplacementGrid({department: cfg.department}),
                ]
            }
        );

        judicial.replacement.ExecutionOrganReplacement.superclass.constructor.call(this, cfg);
    }
});
