
Ext.ns('toolkit.gfp');

Ext.apply(
    toolkit.gfp,
    {
        PensaoEvento: Ext.extend(
            Ext.Window,
            {
                getGridEventos: function() {
                    if(!this.gridEventos) {
                        this.gridEventos = new Ext.grid.GridPanel({
                            region: 'center',
                            minHeight: 100,
                            height: 100,
                            autoExpandColumn: 'autoExpandId',
                            store: new Ext.data.JsonStore({
                                data: this.config.eventos,
                                fields: ['pk', 'chave', 'descricao', 'valor']
                            }),
                            cm: new Ext.grid.ColumnModel([
                                {
                                    dataIndex: 'chave',
                                    header: 'Número',
                                    width: 60
                                },
                                {
                                    dataIndex: 'descricao',
                                    header: 'Descrição',
                                    id: 'autoExpandId'
                                },
                                {
                                    dataIndex: 'valor',
                                    header: 'Valor',
                                    width: 80,
                                    renderer: toolkit.util.formatCurrency
                                }
                            ])
                        });
                        
                        this.gridEventos.getSelectionModel().lock();
                    }
                    
                    return this.gridEventos;
                },
                
                getGridBeneficiarios: function() {
                    if(!this.gridBeneficiarios) {
                        this.gridBeneficiarios = new Ext.grid.GridPanel({
                            title: 'Selecione um beneficiário',
                            region: 'south',
                            split: true,
                            minHeight: 100,
                            height: 150,
                            listeners: {
                                render: function(g) {
                                    new Ext.LoadMask(
                                        g.getEl(),
                                        {
                                            msg: 'Carregando beneficiário...',
                                            store: g.getStore()
                                        }
                                    );
                                    
                                    g.getStore().load({});
                                }
                            },
                            store: new Ext.data.JsonStore({
                                url: toolkit.util.Normalize.controller_action('GFPLancador', 'list_pensao_morte'),
                                baseParams: {
                                    folha: this.config.folha,
                                    servidor: this.config.servidor
                                },
                                root: 'root',
                                fields: ['pk', 'nome']
                            }),
                            autoExpandColumn: 'autoExpandId',
                            cm: new Ext.grid.ColumnModel([
                                {
                                    dataIndex: 'nome',
                                    id: 'autoExpandId',
                                    header: 'Nome do beneficiário'
                                },
                                {
                                    dataIndex: 'valor',
                                    header: 'Rendimento',
                                    width: 80,
                                    renderer: toolkit.util.formatCurrency,
                                    menuDisabled: true
                                }
                            ]),
                            sm: new Ext.grid.RowSelectionModel({singleSelect: true})
                        });
                    }
                    
                    return this.gridBeneficiarios;
                },
                
                save: function() {
                    var selection = this.getGridBeneficiarios().getSelectionModel().getSelected();;
                    
                    if(selection) {
                        var store = this.getGridEventos().getStore();
                        var params = {
                            pensao: selection.get('pk'),
                            folha_eventos: []
                        }
                        
                        store.each(function(record) { params.folha_eventos.push(record.get('pk')); });
                        var stats = new Ext.LoadMask(this.getEl(), {msg: 'Associando evento ao beneficiário.'});
                        stats.show();
                        
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action('PENSAOGerenciadorPensao', 'associa_evento_debito'),
                            params: params,
                            success: function(request) {
                                var obj = Ext.decode(request.responseText);
                                
                                stats.hide();
                                if(obj.success) {
                                    if(this.config.callback) {
                                        var scope = this.config.scope ? this.config.scope : window
                                        this.config.callback.call(scope);
                                    }
                                    
                                    this.destroy();
                                }
                                else 
                                    if(obj.messages.length > 0 && obj.messages.length < 3)
                                        Ext.each(obj.messages, function(msg) { alert(msg) } )
                                    else if(obj.messages.length > 0) {
                                        var msg = 'Ocorreram erros processando a sua solicitação, não consegui atender para os eventos: ';
                                        Ext.each(obj.evento_error, function(evento) { msg += evento });
                                        alert(msg);
                                    }
                                    else
                                        alert(obj.message)
                            },
                            failure: function(request) {
                                alert('Erro processando sua solicitação. Tente novamente mais tarde.')
                                stats.hide();
                            },
                            scope: this
                        })
                    }
                    else alert('Selecione um beneficiário para receber o débito.');
                    
                    console.debug(params);
                },
                
                constructor: function(cfg) {
                    var cf = {
                        title: 'Associar debito a beneficiário',
                        closable: true,
                        modal: true,
                        resizable: false,
                        width: 450,
                        height: 300,
                        layout: 'border',
                        border: false,
                        buttons: [
                            {
                                text: 'Associar',
                                scope: this,
                                handler: this.save
                            },
                            {
                                text: 'Cancelar',
                                handler: this.destroy,
                                scope: this
                            }
                        ],
                        config: cfg
                    };
                    
                    toolkit.gfp.PensaoEvento.superclass.constructor.call(this, cf);
                    
                    this.add(this.getGridEventos());
                    this.add(this.getGridBeneficiarios());
                }
            }
        ),
        
        PensaoView: Ext.extend(
            Ext.Window,
            {
                constructor: function(cf) {
                    Ext.apply(cf, {
                        modal: true,
                        closable: true,
                        width: 700,
                        height: 500,
                        layout: 'border',
                        border: false
                    });
                    
                    if(!cf.config) 
                        throw "Configurações não foram definidas."
                    else if(!cf.config.folha) 
                        throw "Folha de pagamento não foi definida."
                    else if(!cf.config.servidor)
                        throw "Servidor não foi definido."
                    
                    toolkit.gfp.PensaoView.superclass.constructor.call(this, cf);
                    
                    this.add(this.getGridPanel());
                    this.add(this.getGridEventos());
                },
                
                getServidorSource: function() {
                    throw "Not implemented";
                },
                
                getEventosSource: function() {
                    throw "Not implemented";
                },
                
                getGridEventos: function() {
                    if(!this.eventosPanel) {
                        var store = new Ext.data.JsonStore({
                            url: this.getEventosSource(),
                            baseParams: { folha: this.config.folha },
                            root: 'root',
                            fields: ['pk', 'description', 'pct', 'prazo', 'valor',  'valor_base']
                        });
                        
                        this.eventosPanel = new Ext.grid.GridPanel({
                            store: store,
                            region: 'south',
                            height: 200,
                            minHeight: 150,
                            maxHeight: 300,
                            split: true,
                            autoExpandColumn: 'autoExpandId',
                            cm: new Ext.grid.ColumnModel([
                                {
                                    header: 'Descrição',
                                    id: 'autoExpandId',
                                    dataIndex: 'description',
                                    sortable: true
                                },
                                {
                                    header: 'Percentual',
                                    menuDisabled: true,
                                    dataIndex: 'pct',
                                    width: 80,
                                    renderer: function(value) {
                                        return '<p style="text-align:center">' + value + ' %</p>'
                                    }
                                },
                                {
                                    header: 'Prazo',
                                    menuDisabled: true,
                                    dataIndex: 'prazo',
                                    width: 80,
                                    renderer: function(value) {
                                        return '<p style="text-align:center">' + value + ' </p>'
                                    }
                                },
                                {
                                    header: 'Valor',
                                    menuDisabled: true,
                                    dataIndex: 'valor',
                                    width: 80,
                                    renderer: toolkit.util.formatCurrency
                                },
                                {
                                    header: 'Valor Base',
                                    menuDisabled: true,
                                    dataIndex: 'valor_base',
                                    width: 80,
                                    renderer: toolkit.util.formatCurrency
                                }
                            ]),
                            bbar: new Ext.PagingToolbar({store: store}),
                            listeners: {
                                render: function(g) {
                                    new Ext.LoadMask(
                                        g.getEl(),
                                        {
                                            msg: 'Carregando eventos do beneficiário...',
                                            store: g.getStore()
                                        }
                                    );                                    
                                }
                            }
                        });
                    }
                    
                    return this.eventosPanel;
                },
                
                getGridPanel: function() {
                    if(!this.gridPanel) {
                        var store = new Ext.data.JsonStore({
                            url: this.getServidorSource(),
                            baseParams: {
                                servidor: this.config.servidor,
                                folha: this.config.folha
                            },
                            root: 'root',
                            fields: ['pk', 'nome', 'valor', 'data_fim']
                        });
                        
                        this.gridPanel = new Ext.grid.GridPanel({
                            store: store,
                            border: true,
                            region: 'center',
                            autoExpandColumn: 'autoExpand',
                            sm: new Ext.grid.RowSelectionModel({
                                single: true,
                                listeners: {
                                    scope: this,
                                    rowselect: function(sm, index, record) {
                                        var store = this.getGridEventos().getStore();
                                        store.baseParams.pensao = record.get('pk');
                                        
                                        console.debug(store.baseParams);
                                        
                                        store.load({});
                                    }
                                }
                            }),
                            cm: new Ext.grid.ColumnModel([
                                {
                                    header: 'Nome',
                                    dataIndex: 'nome',
                                    id: 'autoExpand'
                                },
                                {
                                    header: 'Fim do Vinculo',
                                    dataIndex: 'data_fim',
                                    width: 100,
                                    menuDisabled: true
                                },
                                {
                                    header: 'Valor',
                                    dataIndex: 'valor',
                                    width: 100,
                                    menuDisabled: true,
                                    renderer: toolkit.util.formatCurrency
                                }
                            ]),
                            listeners: {
                                scope: this,
                                render: function(g) {
                                    new Ext.LoadMask(
                                        g.getEl(),
                                        {
                                            store: g.getStore(),
                                            msg: 'Aguarde carregando beneficiários...'
                                        }
                                    );
                                    
                                    g.getStore().load({});
                                }
                            },
                            bbar: new Ext.PagingToolbar({store: store})
                        });
                    }
                    
                    return this.gridPanel;
                }
            }
        ),
    }
);

Ext.apply(
    toolkit.gfp,
    {
        
        PensaoAlimenticiaView: Ext.extend(
            toolkit.gfp.PensaoView,
            {
                constructor: function(cf) {
                    Ext.apply(
                        cf, 
                        {
                            title: 'Visualizar Pensões Alimenticias'
                        }
                    );
                    
                    toolkit.gfp.PensaoAlimenticiaView.superclass.constructor.call(this, cf);
                },
                
                getEventosSource: function() {
                    return toolkit.util.Normalize.controller_action(
                        'GFPLancador',
                        'list_pensao_eventos',
                        ['pa']
                    );
                },
                
                getServidorSource: function() {
                    return toolkit.util.Normalize.controller_action(
                        'GFPLancador',
                        'list_pensao_alimentacao'
                    );
                }
            }
        ),
        
        PensaoMorteView: Ext.extend(
            toolkit.gfp.PensaoView,
            {
                constructor: function(cf) {
                    Ext.apply(
                        cf, 
                        {
                            title: 'Visualizar Pensões por Morte'
                        }
                    );
                    
                    toolkit.gfp.PensaoMorteView.superclass.constructor.call(this, cf);
                },
                
                getEventosSource: function() {
                    return toolkit.util.Normalize.controller_action(
                        'GFPLancador',
                        'list_pensao_eventos',
                        ['pm']
                    );
                },
                
                getServidorSource: function() {
                    return toolkit.util.Normalize.controller_action(
                        'GFPLancador',
                        'list_pensao_morte'
                    );
                }
            }
        ),
        
    }
)