/**
 *
 */

Ext.ns('rh.gfp.lancador');

rh.gfp.lancador.Pendencies = Ext.extend(
    Ext.Window,
    {
        'setRequest': function(request) {
            this._request = request;
            Ext.apply(
                this.getStore().baseParams,
                {'solicitacao': request}
            );

            if(this._request)
                this.getStore().load({});
            else
                this.getStore().removeAll();
        },

        'reload': function() {
            this.getStore().reload()
        },

        'getColumnModel': function() {
            if(!this._columnModel)
                this._columnModel = new Ext.grid.ColumnModel({
                    // specify any defaults for each column
                    defaults: {
                        sortable: true // columns are not sortable by default
                    },
                    columns: [{
                        id: 'pk',
                        header: 'Código',
                        dataIndex: 'pk',
                        width: 80
                    },{
                        id: 'autoExpandColumn',
                        header: 'Contracheque',
                        dataIndex: 'contracheque',
                        width: 300
                    },{
                        id: 'resumo',
                        header: 'Resumo',
                        dataIndex: 'resumo',
                        width: 200
                    },{
                        // xtype: 'checkcolumn',
                        header: 'Conferido',
                        dataIndex: 'conferido',
                        width: 55
                    }]
                });
            console.debug('getColumnModel...');
            return this._columnModel;
        },

        'confirmAllPendenting': function(){
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action('GFPControlador', 'confirm'),
                params: {folha: this.folha.pk, evento: (this.evento? this.evento.pk: null)},
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(!obj.success){
                        Ext.Msg.show({
                            icon: Ext.Msg.ERROR,
                            msg: obj.message,
                            buttons: Ext.Msg.OK
                        });
                    }else{
                        this.reload();
                    }                        },
                failure: function() {alert('Ocorreu um erro tentando remover os lançamentos.');},
                scope: this
            });
            // }
            // else alert('Primeiro selecione as mudanças a serem confirmadas.');
        },

        'confirmSelecteds': function(){
            var selections = this.getPendingEventsGrid().getSelectionModel().getSelections();
            if(selections.length > 0) {
                var fes = [];

                Ext.each(selections, function(fe) {fes.push(fe.get('pk'));});

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPControlador', 'confirm'),
                    params: {folha: this.folha.pk, folhaeventos: fes},
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(!obj.success){
                            Ext.Msg.show({
                                icon: Ext.Msg.ERROR,
                                msg: obj.message,
                                buttons: Ext.Msg.OK
                            });
                        }else{
                            this.reload();
                        }                        },
                    failure: function() {alert('Ocorreu um erro tentando remover os lançamentos.');},
                    scope: this
                });
            }
            else alert('Selecione os lançamentos a serem confirmadas.');
        },

        'getToolbar': function() {
            if(!this._toolbar)
                this._toolbar = new Ext.Toolbar({
                    'items': [
                        {
                                text: 'Confirmar Pendências',
                                menu:[
                                    {
                                        'text': 'Todos',
                                        'scope': this,
                                        'handler': this.confirmAllPendenting,
                                        'icon': '/' + global.Context + '/static/rh/images/folha-validar.png',
                                    },
                                    {
                                        'text': 'Selecionados',
                                        'scope': this,
                                        'handler': this.confirmSelecteds,
                                        'icon': '/' + global.Context + '/static/rh/images/folha-validar.png',
                                    },

                                ]
                        },
                        '-',
                        // {
                        //     'text': 'Todos',
                        //     'enableToggle': true,
                        //     'toggleHandler': this.changeFilter,
                        //     'pressed': false,
                        //     'scope': this,
                        // },
                        // '->',
                        // '-',
                        // {
                        //     'iconCls': 'icon-diarias icon-refresh',
                        //     'scope': this,
                        //     'handler': this.reload
                        // }
                    ]
                });

            return this._toolbar;
        },

        'getStore': function() {
            if(!this._store) {
                this._store = new Ext.data.Store({
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action(
                            'GFPControlador', 'pendencies'
                        ),
                        'method': 'POST',
                        // 'disableCaching': false
                    }),
                    'reader': new Ext.data.JsonReader({
                        'root': 'root',
                        'totalProperty': 'totalRows',
                        'fields': [
                            {'name': 'pk', 'type': 'int'},
                            {'name': 'servidor', 'type': 'string'},
                            {'name': 'evento', 'type': 'string'},
                            {'name': 'qnt', 'type': 'string'},
                            {'name': 'pct', 'type': 'string'},
                            {'name': 'valor', 'type': 'string'},
                            {'name': 'prazo', 'type': 'string'},
                            {'name': 'patronal', 'type': 'string'},
                            {'name': 'info', 'type': 'string'},
                        ],
                        // 'baseParams': {
                        //     folha: this.folha.pk,
                        //     // all: false
                        // }
                    })
                });
            }
            console.debug('getStore...');

            return this._store;
        },

        'getPendingEventsGrid': function() {
            if(!this._pendingEvents) {
                console.debug('getPendingEventsGrid...');
                this._pendingEvents = new Ext.grid.GridPanel({
                    region: 'center',
                    split: false,
                    'tbar': this.getToolbar(),
                    'store': this.getStore(),
                    'autoExpandColumn': 'autoExpand',
                    'iconCls': 'icon-grid',
                    // 'viewConfig': {
                    //     'forceFit':true
                    // },
                    'bbar': new Ext.PagingToolbar({
                            store: this.getStore(),
                            displayInfo: true,
                            pageSize: 50
                    }),
                    'cm': new Ext.grid.ColumnModel([
                            { header: 'Servidor', dataIndex: 'servidor', id: 'autoExpand'},
                            { header: 'Evento', dataIndex: 'evento', width: 200},
                            { header: 'Qtd', dataIndex: 'qnt', width: 50, menuDisabled: true },
                            { header: '%', dataIndex: 'pct', width: 50, menuDisabled: true },
                            { header: 'Prazo', dataIndex: 'prazo', width: 65, menuDisabled: true },
                            { header: 'Valor (R$)', dataIndex: 'valor', width: 65, menuDisabled: true },
                            { header: 'Patronal', dataIndex: 'patronal', width: 65, menuDisabled: true },
                    ]),
                    listeners: {
                        'render': function(g) {
                            new Ext.LoadMask(
                                g.getEl(),
                                {
                                    store: g.getStore(),
                                    msg: 'Carregando pendências da folha...'
                                }
                            );
                            // g.getStore().load({});
                        }
                    },
                });
            }
            console.debug('getPendingEventsGrid 2...');

            return this._pendingEvents;
        },

        'getEventoFormPanel': function() {
            if(!this._eventoFormPanel) {

                this._eventoFormPanel = new Ext.form.FormPanel({
                    frame: true,
                    labelAlign: 'left',
                    region: 'north',
                    height: 40,
                    split: false,
                    margin: '0 5 5 0',
                    items: [
                        {
                            xtype: 'rest-autocompletefield',
                            fieldLabel: 'Evento',
                            name: 'evento',
                            rest: 'rh.gfp.payroll.EventRestful',
                            width: 500,
                            tabIndex: 1,
                            enableKeyEvents: true,
                            comboListeners: {
                                scope: this,
                                select: function(cmb, rec, idx) {
                                    this.evento = rec.data
                                    this.getStore().setBaseParam('evento', this.evento.pk);
                                    this.getStore().load()
                                },
                                clear: function(cmb){
                                    this.evento = null
                                    this.getStore().setBaseParam('evento', cmb.evento);
                                    this.getStore().load()
                                },
                                keypress: function(cmb, e){
                                    if(e.charCode==13 & cmb.getRawValue()==''){
                                        cmb.reset();
                                        this.evento = null;
                                        this.getStore().setBaseParam('evento', null);
                                        this.getStore().load();
                                    }
                                }
                            },
                        }
                    ],
                    scope: this
                });
            }
            return this._eventoFormPanel;
        },

        'constructor': function(cfg) {
            cfg = (cfg ? cfg : {});
            // console.debug(cfg);
            Ext.apply(cfg, {
                'title': 'Pendências na Folha de Pagamento [ '+ (cfg.folha? cfg.folha.description: '') +' ]',
                'layout': 'border',
                'height': 600,
                'width': 800,
                tbar: this.getToolbar(),
                'items': [
                    this.getEventoFormPanel(),
                    this.getPendingEventsGrid(),
                    // this.getDisplayPanel()
                ],
                'listeners': {
                    'scope': this,
                    'render': function() {
                        console.debug('RENDER ....');
                        this.getStore().load({});
                    }
                }
            });

            rh.gfp.lancador.Pendencies.superclass.constructor.call(this, cfg);

            this.getStore().setBaseParam('folha', this.folha.pk);

        }
    }
);