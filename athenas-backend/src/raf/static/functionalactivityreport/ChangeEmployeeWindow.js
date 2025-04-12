
Ext._define('raf.functionalactivityreport.ChangeEmployeeWindow', {
    extend: 'Ext.Window',

    getEmployeeGrid: function(cfg) {
        if(!this._employeeGrid) {
            var me = this;
            this._employeeGrid = Ext._create('raf.EmployeeGrid', {
                 region: 'center',
                 gridAutoLoad: true,
                 columnAction: false,
                 hideItemsToolbar: ['add', 'edit', 'copy', 'remove', '-', 'download', '->', 'filtro'],
                 hiddenFilter: true,
                 storeDefaultRoute: 'employee_trust_relation',
                 hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'first_adjustment_date'],
                 doubleClickHandler: function(){
                    var employee = me.employeeSelected();

                    core.invokeCallback((me.callback || {}).success, employee);
                    me.close();
                 },
                 sm: new Ext.grid.RowSelectionModel({singleSelect:true})
            });

            this._employeeGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    this.employeeSelected();
                }
            });

            // this._employeeGrid.setFilterProperty('ativo', true, 2000, false);
            // this._employeeGrid.setFilterProperty('tipo', 'M', 2001);

        }

        return this._employeeGrid;
    },

    employeeSelected: function() {
        var selected = this.getEmployeeGrid().getSelectionModel().getSelected();

        return selected;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [

                {
                    text: 'Selecionar',
                    scope: this,
                    handler: function() {
                        var employee = this.employeeSelected();

                        core.invokeCallback((this.callback || {}).success, employee);
                        this.close();
                    }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Membros com relação de confiança',
                modal: true,
                width: Ext.getBody().getBox().width * 0.4,
                height: Ext.getBody().getBox().height * 0.65
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                buttons: this.getButtons(),
                items: [
                    this.getEmployeeGrid(cfg)
                ]
            }
        );

        raf.functionalactivityreport.ChangeEmployeeWindow.superclass.constructor.call(this, cfg);
    }
});
