
Ext._define('raf.trustrelationship.Launcher', {
    extend: 'toolkit.widget.TabPanel',

    getEmployeeGrid: function() {
        if(!this._employeeGrid) {
            this._employeeGrid = Ext._create('raf.EmployeeGrid', {
                region: 'north',
                title: 'Membros',
                split: true,
                height: 300,
                minHeight: 250,
                maxHeight: 650,
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search'],
                hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode'],
                hideItemsToolbar: ['add', 'edit', 'copy', 'remove', '-', 'download', 'filtro'],
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true})
            });

            this._employeeGrid.setFilterProperty('ativo', true, 2000, false);
            this._employeeGrid.setFilterProperty('tipo', 'M', 2001);

            this._employeeGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.relationship(selection[0].get('pk'));
                    else
                        this.relationship(null);
                }
            });

        }

        return this._employeeGrid;
    },

    getTrustRelationshipGrid: function() {
        if(!this._relationshipGrid)
            this._relationshipGrid = Ext._create('raf.trustrelationship.Grid', {
                region: 'center',
                title: 'Servidores com Relação de Confiança',
                disabled: true,
                gridAutoLoad: false,
                hideItemsToolbar: ['remove'],
                columnAction: false,
            });

        return this._relationshipGrid;
    },

    relationship: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._relationship = value;

            if(dispatch) this.observeRelationship();
        }

        return this._relationship;
    },

    observeRelationship: function() {
        var value = this.relationship();
        if(value) {

            this.getTrustRelationshipGrid().enable();
            this.getTrustRelationshipGrid().setParam('employee', value);
            this.getTrustRelationshipGrid().setFilterProperty('employee', value, 1000);

        } else {
            this.getTrustRelationshipGrid().disable();
            this.getTrustRelationshipGrid().setParam('employee', 0);
            this.getTrustRelationshipGrid().removeFilterProperty('employee', 1000, false);
            this.getTrustRelationshipGrid().getStore().removeAll();
        }
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Relação de Confiança'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getEmployeeGrid(),
                    this.getTrustRelationshipGrid()
                ]
            }
        );

        raf.trustrelationship.Launcher.superclass.constructor.call(this, cfg);

        this.observeRelationship();
    }
});
