/**
 *
 **/

Ext._define('workflow.workflow.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getWorkflowGrid: function() {
		if(!this._workflowGrid) {
			this._workflowGrid = Ext._create('workflow.workflow.Grid', {
				hideItemsToolbar: ['remove', 'search', 'download'],
				columnAction: false,
                allowRemove: false,
                maxWidth: Ext.getBody().getBox().width * 0.22,
                minWidth: Ext.getBody().getBox().width * 0.20,
                width: Ext.getBody().getBox().width * 0.20,
                region: 'center',
				sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
			});

			this._workflowGrid.getSelectionModel().on({
			    scope: this,
			    selectionchange: function(selm) {
			        var selection = selm.getSelections();

			        if(selection.length > 0)
			            this.workflow(selection[0]);
			        else
			            this.workflow(null);
			    }
			});
		}

		return this._workflowGrid;
	},

	workflow: function(value, dispatch) {
	    dispatch = (dispatch === undefined ? true : dispatch);

	    if(value !== undefined) {
	        this._workflow = value;

	        if(dispatch)
	            this.observeWorkflow();
	    }

	    return this._workflow;
	},

	observeWorkflow: function() {
	    var value = this.workflow();

	    if(value) {
	        this.getVertexGrid().enable();
	        this.getVertexGrid().setParam('workflow', value.get('pk'));
	        this.getVertexGrid().setFilterProperty('workflow', value.get('pk'), 1001);
	    }
	    else {
	        this.getVertexGrid().disable();
	        this.getVertexGrid().setParam('workflow', 0);
	        this.getVertexGrid().setFilterProperty('workflow', 0, 1001, false);
	        this.getVertexGrid().getStore().removeAll();
	    }
	},

	getVertexGrid: function(cfg) {
        if(!this._vertexGrid) {
            this._vertexGrid = Ext._create('workflow.vertex.Grid', {
				columnAction: false,
                title: 'Vértices',
                region: 'center',
                gridAutoLoad: false,
                split: true
            });

            this._vertexGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var selection = selm.getSelections();

                    if(selection.length > 0)
                        this.vertex(selection[0]);
                    else
                        this.vertex(null);
                }
            });
        }

        return this._vertexGrid;
    },

    vertex: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._vertex = value;

            if(dispatch)
                this.observeVertex();
        }

        return this._vertex;
    },

	observeVertex: function() {
	    var value = this.vertex();

	    if(value) {
	        this.getEdgeGrid().enable();
	        this.getEdgeGrid().setParam('source', value.get('pk'));
			this.getEdgeGrid().setParam('workflow', this.getVertexGrid().params.workflow);
	        this.getEdgeGrid().setFilterProperty('source', value.get('pk'), 1002);
	    }
	    else {
	        this.getEdgeGrid().disable();
	        this.getEdgeGrid().setParam('source', 0);
			this.getEdgeGrid().setParam('workflow', 0);
	        this.getEdgeGrid().setFilterProperty('source', 0, 1002, false);
	        this.getEdgeGrid().getStore().removeAll();
	    }
	},

    getEdgeGrid: function(cfg) {
        if(!this._edgeGrid) {
            this._edgeGrid = Ext._create('workflow.edge.Grid', {
				columnAction: false,
                title: 'Arestas',
                region: 'east',
                gridAutoLoad: false,
                minWidth: Ext.getBody().getBox().width * 0.33,
                maxWidth: Ext.getBody().getBox().width * 0.35,
                width: Ext.getBody().getBox().width * 0.35,
                split: true
            });
		}

        return this._edgeGrid;
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Workflows'
			}
		);

		Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getWorkflowGrid(),
                    {
                        xtype: 'panel',
                        region: 'east',
                        layout: 'border',
                        border: false,
                        minWidth: Ext.getBody().getBox().width * 0.78,
                        maxWidth: Ext.getBody().getBox().width * 0.80,
                        width: Ext.getBody().getBox().width * 0.78,
                        split: true,
                        items: [
	                    	this.getVertexGrid(),
	                    	this.getEdgeGrid(),
                        ]
	                }
                ]
            }
        );

		workflow.workflow.Manage.superclass.constructor.call(this, cfg);
		this.observeWorkflow();
		this.observeVertex();
	}
});
