Ext._define('planning.hiring.enterprise.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getEnterpriseGrid: function() {
        if(!this._enterpriseGrid) {
            this._enterpriseGrid = Ext._create('planning.hiring.enterprise.Grid', {
                region: 'center'
            });

            this._enterpriseGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function (selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this.enterprise(selection[0].id);
                    } else {
                        this.enterprise(null);
                    }
                }
            });

            this._enterpriseGrid.getStore().on({
                scope: this,
                load: function () {
                    this.observeEnterprise();
                }
            });
        }

        return this._enterpriseGrid;
    },

    enterprise: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._enterprise = value;

            if (observe)
                this.observeEnterprise();
        }

        return this._enterprise;
    },

    observeEnterprise: function() {
        var value = this.enterprise();
        var selected = this.getEnterpriseGrid().getSelectionModel().getSelected();
        // enterprise = 0
        // if(selected != null)
        //     enterprise = selected.data.enterprise;
        var corporateStructureGrid = this.getCorporateStructureGrid();

        if(value) {
            corporateStructureGrid.enable();
            // corporateStructureGrid.setParam('ride', value);
            // corporateStructureGrid.setParam('minute', minute);
            corporateStructureGrid.setFilterProperty('enterprise', value, 10);
        } else {
            corporateStructureGrid.disable();
            // corporateStructureGrid.setParam('ride', 0);
            // corporateStructureGrid.setParam('minute', 0);
            corporateStructureGrid.getStore().removeAll();
            corporateStructureGrid.setFilterProperty('enterprise', value, 10, false);
        }
    },

    getCorporateStructureGrid: function() {
        if(!this._corporateStructureGrid) {
            this._corporateStructureGrid = Ext._create('planning.hiring.corporatestructure.Grid', {
                title: 'Sócios',
                region: 'south',
                height: 300,
                gridAutoLoad: false
            });
        }

        return this._corporateStructureGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});[]

        Ext.applyIf(
            cfg,
            {
                title: 'Gerência de Estrutura Societária',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getEnterpriseGrid(),
                    // this.getCorporateStructureGrid()
                ]
            }
        );

        planning.hiring.enterprise.Manage.superclass.constructor.call(this, cfg);
        this.observeEnterprise();
    }
});
