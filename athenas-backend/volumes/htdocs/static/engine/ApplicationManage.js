/**
 *
 **/
Ext._define('engine.ApplicationManage', {
    'extend': 'toolkit.widget.TabPanel',

    'observe': function() {
        if(this._applicationId > 0) {
            this.getControllerGrid().setFilterProperty(
                'application',
                this._applicationId,
                100
            );
            this.getControllerGrid().setParam('application', this._applicationId);
            this.getControllerGrid().enable();
        }
        else {
            this.getControllerGrid().setFilterProperty(
                'application',
                0,
                100
            );
            this.getControllerGrid().setParam('application', 0);
            this.getControllerGrid().disable();
        }
    },

    'setApplicationId': function(value) {
        this._applicationId = Number(value);
        this.observe();
    },

    'getApplicationId': function() {
        return this._applicationId;
    },

    'getApplicationTreePanel': function() {
        if(!this._applicationTreePanel) {
            this._applicationTreePanel = Ext._create('engine.ApplicationTree', {
                'region': 'west',
                'rootVisible': true,
                'split': true,
                'width': 300,
                'maxWidth': 400,
                'minWidth': 200
            });

            this._applicationTreePanel.getSelectionModel().on({
                'scope': this,
                'selectionchange': function(tree, node) {
                    this.setApplicationId(node.id);
                }
            })
        }

        return this._applicationTreePanel;
    },

    'getControllerGrid': function() {
        if(!this._controllerGrid)
            this._controllerGrid = Ext._create('engine.ControllerGrid', {
                'xtype': 'panel',
                'region': 'center',
                'gridAutoLoad': false
            });

        return this._controllerGrid;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'title': 'Gestor de Funcionalidades'
            }
        );

        Ext.apply(
            cfg,
            {
                'layout': 'border',
                'border': false,
                'items': [
                    this.getApplicationTreePanel(),
                    this.getControllerGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        engine.ApplicationManage.superclass.constructor.call(this, cfg);
        this.observe();
    }
});
