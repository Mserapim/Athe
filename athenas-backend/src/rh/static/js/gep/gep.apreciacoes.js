Ext.ns('toolkit.gep');


toolkit.gep.Apreciacoes = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg){
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title:'Apreciações da Comissão',
                closable: true,
                autoScroll: true,
                modal: true,
                width: 600,
                height: 300,
                border: false,
                items:this.getGrid()

            });

            toolkit.gep.Medias.superclass.constructor.call(this, cfg);
        },

        getGrid: function(){
            if(!this._grid){
                this._grid = new Ext.grid.GridPanel({
                    scope:this,
                    columnLines: true,
                    autoWidth:true,
                    // width: 520,
                    height: 260,
                    store: this.getStore(),
                    bbar: this.getPagingToolbar(),
                    columns:[
                        new Ext.grid.RowNumberer(),
                        {
                            dataIndex:'integrante_comissao', 
                            header:'Integrante da Comissão', 
                            width:260
                        },
                        {
                            dataIndex:'decisao', 
                            header:'Decisão', 
                            width:220
                        },
                        {
                            dataIndex:'data', 
                            header:'Data', 
                            width:80
                        },
                    ],
                    listeners: {
                        'scope': this,
                        'render': function(grid) {
                            new Ext.LoadMask(grid.getEl(), {
                                'store': grid.getStore(),
                                'msg': 'Carregando dados...'
                            });
                        }
                    }
                });

            }
            return this._grid;
        },

        getStore: function() {
            if(!this._store)
            {
                this._store = new Ext.data.JsonStore({
                    autoLoad:false,
                    root: 'collection',
                    totalProperty: 'totalRows',
                    fields: [
                        'pk',
                        'integrante_comissao',
                        'decisao',
                        'data',
                    ],
                    url: toolkit.util.Normalize.controller_action('GEPApreciacaoComissao','list_apreciacoes'),
                    baseParams:{
                        start:0,
                        limit:50
                    },
                    scope:this
                });
            }
            return this._store;
        },

        getParams: function() {
            return this.params;
        },

        getPagingToolbar: function() {
            if(!this._pagingToolbar)
            {
                this._pagingToolbar = new Ext.PagingToolbar({
                    style: 'border-right:none',
                    store: this.getStore(),
                    displayInformation: true,
                    pageSize: 50,
                    prependButtons: true
                });
            }
        
            return this._pagingToolbar;
        },
    }
);