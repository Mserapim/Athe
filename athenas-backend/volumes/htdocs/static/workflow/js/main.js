// var vroot = '/'+CONTEXT+'/';
// var mroot = vroot+'static/';
// var icons = mroot+'/workflow/icons/';
Ext.ns('toolkit.workflow');
toolkit.workflow.icons = '/' + CONTEXT + '/static/workflow/icons/';

toolkit.workflow.delete = function(grid, url, params)
{
    var loading = new xt.LoadMask(grid.getEl(), {msg:'Por favor aguarde...', store:grid.getStore()});
    loading.show();
    Ext.Ajax.request({
        url:action(url),
        params: params,
        success:function(response, options)
        {
            loading.hide();
            json = Ext.decode(response.responseText);
            if(!json.success)
                xAlert(json.msg);
            else
                grid.getStore().reload();
        }
    });
};

toolkit.workflow.Workflow = Ext.extend(Ext.Window, {
    constructor: function()
    {
        toolkit.workflow.Workflow.superclass.constructor.call(this, {
            title:'Fluxogramas',
            layout:'fit',
            height: 350,
            width: 500,
            closable:true,
            items:[this._getWorkflowsGrid()],
            tbar:[
                {
                    tooltip:'Criar fluxograma.',
                    icon: toolkit.workflow.icons+'add.png',
                    text: 'Novo',
                    handler: function()
                    { this._makeForm({title:'Criar fluxograma', vals:{}}).show(); },
                    scope:this
                }
            ],
            bbar:[this._getWorkflowsPagination()],
            listeners:{
                show:function()
                { new Ext.LoadMask(this.getEl(), {msg:'Por favor aguarde...', store:this._getWorkflowsStore()}); }
            }
        });
    },

    _getWorkflowsStore: function()
    {
        if(!this._workflowsStore)
        {
            this._workflowsStore = new Ext.data.JsonStore({
                autoLoad:true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'name', 'description'],
                proxy: new Ext.data.HttpProxy({
                    method:'GET',
                    url: action('WWorkflow/list/json')
                }),
                scope:this
            });
        }
        return this._workflowsStore;
    },

    _getWorkflowsGrid: function()
    {
        if(!this._workflowsGrid)
        {
            this._workflowsGrid = new Ext.grid.GridPanel({
                scope:this,
                region:'center',
                border:true,
                store: this._getWorkflowsStore(),
                columns:
                [
                    {dataIndex:'name', header:'Fluxograma', width:368},
                    {
                        xtype: 'actioncolumn',
                        header:'Controles',
                        width: 80,
                        scope:this,
                        items:
                        [
                            {
                                tooltip:'Grafo',
                                icon: toolkit.workflow.icons+'graph.png',
                                handler:function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    toolkit.workflow.graph = new toolkit.workflow.Graph(record.get('id'), record.get('name'));
                                    toolkit.workflow.graph.show();
                                    this.destroy();
                                },
                                scope:this
                            },
                            {
                                tooltip:'Editar ou visualizar fluxograma',
                                icon: toolkit.workflow.icons+'edit.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    this._makeForm({
                                        title:'Editar fluxograma',
                                        vals:{
                                            id:record.get('id'),
                                            name: record.get('name'),
                                            description:record.get('description')
                                        }
                                    }).show();
                                },
                                scope:this
                            },
                            {
                                tooltip: 'Excluir fluxograma',
                                icon: toolkit.workflow.icons+'delete.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    xConfirm({
                                        title:'Confirmação',
                                        msg:'Confirma a exclusão do fluxograma: '+ record.get('name') +' ?',
                                        fn: function(btn)
                                        { toolkit.workflow.delete(grid, 'Workflow/delete/json', {id:record.get('id')}); }
                                    });

                                },
                                scope:this
                            }
                        ]
                    }
                ]
            });
        }
        return this._workflowsGrid;
    },

    _getWorkflowsPagination: function()
    {
        if(!this._workflowsPagination)
        {
            this._workflowsPagination = new Ext.PagingToolbar({
                store: this._getWorkflowsStore(),
                displayInfo: true,
                pageSize: 15,
                prependButtons: true
            });

        }
        return this._workflowsPagination;
    },

    _makeForm: function(opts)
    {
        return ExtFormHelper({
            url:action('Workflow/create_or_edit/json'),
            store:this._getWorkflowsStore(),
            windowConfig:{
                title:opts.title
            },
            formConfig:{
                autoWidth:true,
                autoHeight:true,
                items:[
                    {
                        id:'id',
                        name:'id',
                        value: opts.vals.id || '',
                        xtype:'hidden'
                    },
                    {
                        id:'name',
                        fieldLabel:'Nome',
                        name:'name',
                        value: opts.vals.name || '',
                        width:350,
                        xtype:'textfield'
                    },
                     {
                        id:'description',
                        fieldLabel:'Descrição',
                        name:'description',
                        value: opts.vals.description || '',
                        width:350,
                        xtype:'textarea'
                    }

                ]
            }
        });
    }
});


/******************************** Graph UI **********************************/
toolkit.workflow.Graph = Ext.extend(Ext.Panel, {
    constructor: function(workflow, title)
    {
        this.workflow = workflow;
        toolkit.workflow.Graph.superclass.constructor.call(this, {
            title:'Vertices do fluxograma '+ title,
            layout:'fit',
            height: 350,
            width: 500,
            closable:true,
            items:[this._getVerticesGrid()],
            tbar:[
                {
                    tooltip:'Criar vértice.',
                    icon: toolkit.workflow.icons+'add.png',
                    text: 'Novo',
                    handler: function()
                    { this._makeForm({title:'Criar vértice', vals:{workflow:this.workflow}}).show(); },
                    scope:this
                },
                '-',
                {
                    tooltip:'Visulizar grafo completo',
                    icon: toolkit.workflow.icons+'graph.png',
                    text: 'Visão do grafo',
                    handler: function()
                    {
                        Ext.Ajax.request({
                            url: action('WWorkflow/show_graph'),
                            params: { workflow:this.workflow },
                            success:function(response, options)
                            {
                                var text = response.responseText;
                                var graph = new Ext.Window({
                                    title: 'Grafo do fluxograma '+ title,
                                    html:text,
                                    layout:'fit',
                                    maxWidth:500,
                                    maxHeight: 350,
                                    frame:true,
                                    autoScroll:true,
                                    closable:true
                                });
                                //toolkit.Application.tabspace.add(graph);
                                graph.show()
                            }
                        });
                    },
                    scope:this
                }
            ],
            bbar:[this._getVerticesPagination()],
            listeners:{
                show:function(component)
                { new Ext.LoadMask(component.ownerCt.getEl(), {msg:'Por favor aguarde...', store:this._getVerticesStore()}); }
            }
        });

        toolkit.Application.tabspace.add(this);
    },

    _getVerticesStore: function()
    {
        if(!this._verticesStore)
        {
            this._verticesStore = new Ext.data.JsonStore({
                autoLoad:true,
                root: 'result',
                totalProperty: 'total',
                fields: ['id', 'name', 'acronym', 'beginning', 'description', 'kind', 'objective_id', 'objective'],
                proxy: new Ext.data.HttpProxy({
                    method:'GET',
                    url: action('WVertex/list/json')
                }),
                baseParams:{ workflow:this.workflow },
                scope:this
            });
        }
        return this._verticesStore;
    },

    _getVerticesGrid: function()
    {
        if(!this._verticesGrid)
        {
            this._verticesGrid = new Ext.grid.GridPanel({
                scope:this,
                region:'center',
                border:true,
                store: this._getVerticesStore(),
                columns:
                [
                    {dataIndex:'name', header:'Fluxograma', width:350},
                    {dataIndex:'acronym', header:'Abreviatura', width:150},
                    {
                        dataIndex:'beginning',
                        header:'É o ponto inicial?',
                        width:150,
                        renderer:function(val)
                        { return (val) ? 'Sim' : 'Não';  }
                    },
                    {
                        xtype: 'actioncolumn',
                        header:'Controles',
                        width: 80,
                        scope:this,
                        items:
                        [
                            {
                                tooltip:'Adicionar aresta',
                                icon: toolkit.workflow.icons+'graph.png',
                                handler:function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    new toolkit.workflow.Edge(this.workflow, record.get('id'), record.get('name')).show()
                                },
                                scope:this
                            },
                            {
                                tooltip:'Editar ou visualizar vértice',
                                icon: toolkit.workflow.icons+'edit.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    this._makeForm({
                                        title:'Editar vértice',
                                        vals:{
                                            workflow:this.workflow,
                                            id:record.get('id'),
                                            name: record.get('name'),
                                            acronym: record.get('acronym'),
                                            kind: record.get('kind'),
                                            beginning: record.get('beginning'),
                                            description:record.get('description'),
                                            objective_id: record.get('objective_id'),
                                            objective: record.get('objective')
                                        }
                                    }).show();
                                },
                                scope:this
                            },
                            {
                                tooltip: 'Excluir vértice',
                                icon: toolkit.workflow.icons+'delete.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    xConfirm({
                                        title:'Confirmação',
                                        msg:'Confirma a exclusão do vértice: '+ record.get('name') +' ?',
                                        fn: function(btn)
                                        { toolkit.workflow.delete(grid, 'WVertex/delete/json', {id:record.get('id')}); }
                                    });

                                },
                                scope:this
                            }
                        ]
                    }
                ]
            });
        }
        return this._verticesGrid;
    },

    _getVerticesPagination: function()
    {
        if(!this._verticesPagination)
        {
            this._verticesPagination = new Ext.PagingToolbar({
                store: this._getVerticesStore(),
                displayInfo: true,
                pageSize: 15,
                prependButtons: true
            });

        }
        return this._verticesPagination;
    },

    _makeForm: function(opts)
    {
        var kindStore = new Ext.data.JsonStore({
            autoLoad:true,
            fields: ['id', 'name'],
            proxy: new Ext.data.HttpProxy({
                method:'GET',
                url: action('WVertex/kind_list/json')
            })
        });

        var objectiveStore = new Ext.data.JsonStore({
            fields: ['id', 'name'],
            proxy: new Ext.data.HttpProxy({
                method:'GET',
                url: action('WVertex/objective_list/json')
            })
        });

        if (opts.vals.kind)
            objectiveStore.load({params:{canonical_name: opts.vals.kind }});

        return ExtFormHelper({
            url:action('WVertex/create_or_edit/json'),
            store:this._getVerticesStore(),
            windowConfig:{
                title:opts.title
            },
            formConfig:{
                autoWidth:true,
                autoHeight:true,
                items:[
                    {
                        id:'workflow',
                        name:'workflow',
                        value: opts.vals.workflow || '',
                        xtype:'hidden'
                    },
                    {
                        id:'id',
                        name:'id',
                        value: opts.vals.id || '',
                        xtype:'hidden'
                    },
                    {
                        id:'name',
                        fieldLabel:'Nome',
                        name:'name',
                        value: opts.vals.name || '',
                        width:350,
                        xtype:'textfield'
                    },
                    {
                        id:'acronym',
                        fieldLabel:'Abreviatura (No máximo 10 caractéres)',
                        name:'acronym',
                        value: opts.vals.acronym || '',
                        width:350,
                        xtype:'textfield'
                    },
                    {
                        id:'kind',
                        fieldLabel:'Tipo de Vértice',
                        hiddenName:'kind',
                        hiddenValue: opts.vals.kind || '',
                        mode:'local',
                        value: opts.vals.kind || '',
                        xtype:'combo',
                        triggerAction: 'all',
                        width:350,
                        valueField: 'id',
                        displayField: 'name',
                        store: kindStore,
                        listeners:{
                            select:function(combo, record, index)
                            { objectiveStore.load({params:{canonical_name:record.get('id')}}); }
                        }
                    },
                    {
                        id:'objective',
                        fieldLabel:'Alvo',
                        hiddenName:'objective',
                        hiddenValue: opts.vals.objective_id || '',
                        mode:'local',
                        value: opts.vals.objective || '',
                        xtype:'combo',
                        triggerAction: 'all',
                        width:350,
                        valueField: 'id',
                        displayField: 'name',
                        store: objectiveStore
                    },
                    {
                        id:'beginning',
                        fieldLabel:'É o ponto inicial?',
                        name:'beginning',
                        checked: opts.vals.beginning,
                        value: opts.vals.beginning,
                        width:350,
                        xtype:'checkbox'
                    },
                    {
                        id:'description',
                        fieldLabel:'Descrição',
                        name:'description',
                        value: opts.vals.description || '',
                        width:350,
                        xtype:'textarea'
                    }

                ]
            }
        });
    }
});


/******************************** Edges UI **********************************/
toolkit.workflow.Edge = Ext.extend(Ext.Window, {
    constructor: function(workflow, vertex, title)
    {
        this.workflow = workflow;
        this.source = vertex;
        toolkit.workflow.Edge.superclass.constructor.call(this, {
            title:'Arestas de ' + title,
            layout:'fit',
            height: 250,
            width: 580,
            closable:true,
            items:[this._getEdgesGrid()],
            tbar:[
                {
                    tooltip:'Criar aresta.',
                    icon: toolkit.workflow.icons+'add.png',
                    text: 'Nova',
                    handler: function()
                    { this._makeForm({title:'Criar aresta', vals:{ source: this.source }}).show(); },
                    scope:this
                }
            ],
            bbar:[this._getEdgesPagination()],
            listeners:{
                show:function(component)
                { new Ext.LoadMask(component.getEl(), {msg:'Por favor aguarde...', store:this._getEdgesStore()}); }
            }
        });
    },

    _getEdgesStore: function()
    {
        if(!this._edgesStore)
        {
            this._edgesStore = new Ext.data.JsonStore({
                autoLoad:true,
                root: 'result',
                totalProperty: 'total',
                fields: ['edge_hash', 'slug', 'source', 'target', 'target_name'],
                proxy: new Ext.data.HttpProxy({
                    method:'GET',
                    url: action('WEdge/list/json')
                }),
                baseParams:{ source:this.source },
                scope:this
            });
        }
        return this._edgesStore;
    },

    _getEdgesGrid: function()
    {
        if(!this._edgesGrid)
        {
            this._edgesGrid = new Ext.grid.GridPanel({
                scope:this,
                region:'center',
                border:true,
                store: this._getEdgesStore(),
                columns:
                [
                    {dataIndex:'target_name', header:'Alvo', width:250},
                    {dataIndex:'slug', header:'Slug', width:250},
                    {
                        xtype: 'actioncolumn',
                        header:'Controles',
                        width: 60,
                        scope:this,
                        items:
                        [
                            {
                                tooltip:'Editar ou visualizar aresta',
                                icon: toolkit.workflow.icons+'edit.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row)
                                    this._makeForm({
                                        title:'Editar aresta',
                                        vals:{
                                            slug:record.get('slug'),
                                            source:record.get('source'),
                                            target: record.get('target'),
                                            edge_hash:record.get('edge_hash')
                                        }
                                    }).show();
                                },
                                scope:this
                            },
                            {
                                tooltip: 'Excluir aresta',
                                icon: toolkit.workflow.icons+'delete.png',
                                handler: function(grid, row, col)
                                {
                                    var record = grid.getStore().getAt(row);
                                    xConfirm({
                                        title:'Confirmação',
                                        msg:'Confirma a exclusão da aresta: '+ record.get('slug') +' ?',
                                        fn: function(btn)
                                        { toolkit.workflow.delete(grid, 'WEdge/delete/json', {edge_hash: record.get('edge_hash')}); }
                                    });

                                },
                                scope:this
                            }
                        ]
                    }
                ]
            });
        }
        return this._edgesGrid;
    },

    _getEdgesPagination: function()
    {
        if(!this._edgesPagination)
        {
            this._edgesPagination = new Ext.PagingToolbar({
                store: this._getEdgesStore(),
                displayInfo: true,
                pageSize: 15,
                prependButtons: true
            });

        }
        return this._edgesPagination;
    },

    _makeForm: function(opts)
    {
        var arr = [];
        toolkit.workflow.graph._getVerticesStore().each(
            function(record)
            { arr[arr.length] = [record.get('id'), record.get('name')]; }
        );

        console.log(arr);

        return ExtFormHelper({
            url:action('WEdge/create_or_edit/json'),
            store:this._getEdgesStore(),
            windowConfig:{
                title:opts.title
            },
            formConfig:{
                autoWidth:true,
                autoHeight:true,
                items:[
                    {
                        id:'edge_hash',
                        name:'edge_hash',
                        value: opts.vals.edge_hash || '',
                        xtype:'hidden'
                    },
                    {
                        id:'source',
                        name:'source',
                        value: opts.vals.source || '',
                        xtype:'hidden'
                    },
                    {
                        id:'slug',
                        fieldLabel:'Slug',
                        name:'slug',
                        value: opts.vals.slug || '',
                        width:350,
                        xtype:'textfield'
                    },
                    {
                        id:'target',
                        fieldLabel:'Alvo',
                        hiddenName:'target',
                        hiddenValue: opts.vals.target || '',
                        mode:'local',
                        value: opts.vals.target || '',
                        xtype:'combo',
                        triggerAction: 'all',
                        width:350,
                        valueField: 'id',
                        displayField: 'name',
                        store: new Ext.data.ArrayStore({
                            fields:['id', 'name'],
                            data: arr
                        })
                    }

                ]
            }
        });
    }
});
