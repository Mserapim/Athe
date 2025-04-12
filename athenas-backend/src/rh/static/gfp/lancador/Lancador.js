/**
 *
 */

Ext.ns('rh.gfp.lancador');

rh.gfp.lancador.DifferencesWindow = Ext.extend(
    Ext.Window,
    {
        getDifferencesGrid: function(cf) {
            if(!this._differencesGrid) {
                this._differencesGrid = Ext._create('rh.gfp.paycheckdifference.PayCheckDifferenceItemGrid', {
                    hideColumns: ['paycheck__unicode']
                });
			    this._differencesGrid.setParam('difference', cf.difference);
			    this._differencesGrid.setFilterProperty('difference', cf.difference, 100);
                // this._differencesGrid = new rh.gfp.paycheckdifference.PayCheckDifferenceItemGrid(cf);
            }
            return this._differencesGrid;
        },

        getPanel: function(cf){
            if(!this._panel)
                this._panel = new Ext.Panel({
                    width:800,
                    height:350,
                    layout: 'fit',
                    items:[
                        this.getDifferencesGrid(cf),
                    ]
                });
            // this.getDependenciaGrid().disable();
            return this._panel;

        },

        constructor: function(cf) {
            var df = {
                title: 'Diferenças aplicadas',
                scope:this,
                closable: true,
                modal: true,
                border: false,
                items: this.getPanel(cf)
            };
            Ext.apply(cf, df);
            rh.gfp.lancador.DifferencesWindow.superclass.constructor.call(this, cf);
        },
    }
);

rh.gfp.lancador.Lancador = Ext.extend(
    Ext.Panel,
    {

        getStatusBar: function() {
            if(!this.topStatusBar) {
                this.topStatusBar = new Ext.Toolbar({
                    items: [
                        this.getAuditTextItem(),
                        '->',
                        this.getProventosTextItem(),
                        this.getDescontosTextItem(),
                        this.getLiquidoTextItem(),
                        this.getPatronalTextItem()
                    ]
                });
            }

            return this.topStatusBar
        },

        addContracheque: function() {
            console.debug('Função ainda não implementada!');
        },

        removeContracheque: function() {
            var selections = this.getTopGrid().getSelectionModel().getSelections();
            if(selections.length > 0) {
                var fes = [];

                Ext.each(selections, function(fe) {fes.push(fe.get('pk'));});

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPGestorContracheque', 'delete'),
                    params: {pk: this.cfg.pk, folha: this.folha.pk, servidor: this.servidor.pk},
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
                    failure: function() {
                        Ext.Msg.show({
                            icon: Ext.Msg.ERROR,
                            msg: 'Ocorreu um erro tentando apagar o contracheque.',
                            buttons: Ext.Msg.OK
                        });
                    },
                    scope: this
                });
            }
            else
                Ext.Msg.show({
                    icon: Ext.Msg.ERROR,
                    msg: 'Selecione o contracheque a ser apagado.',
                    buttons: Ext.Msg.OK
                });
        },

        addEvento: function() {
            new toolkit.gfp.LancadorEvento({
                folha: this.folha,
                servidor: this.servidor,
                evento: {
                    // pk: selection.data.evento__pk,
                },
                scope: this,
                callback: function() {this.reload();}
            }).show();
        },

        editEvento: function() {
            var selection = this.getCenterGrid().getSelectionModel().getSelected();
            // console.debug(selection);

            if(selection){
                // if(selection.data.evento__automatico!=true){
                // console.debug(selection.data);
                new toolkit.gfp.LancadorEvento({
                    markIfDirty: true,
                    folha: this.folha,
                    servidor: this.servidor,
                    scope: this,
                    evento__pk: selection.data.evento__pk,
                    qnt: selection.data.qnt,
                    parcela: selection.data.parcela,
                    prazo: selection.data.prazo,
                    pct: selection.data.pct,
                    valor: selection.data.valor,
                    valor_base: selection.data.valor_base,
                    patronal: selection.data.patronal,
                    base_previdencia: selection.data.base_previdencia,
                    info: selection.data.info,
                    reference_month: selection.data.reference_month,
                    reference_year: selection.data.reference_year,
                    folhaevento: selection.data.pk,
                    qnt_max: selection.data.qnt_max,
                    evento: {
                        pk: selection.data.evento__pk,
                        automatico: selection.data.evento__automatico,
                        qnt_max: selection.data.qnt_max
                    },
                    paycheck_difference: selection.data.paycheck_difference,
                    paycheck_difference__unicode: selection.data.paycheck_difference__unicode,
                    status_entry: selection.data.status_entry,
                    correct_valor: selection.data.correct_valor,
                    diff_valor_aprovisionado: selection.data.diff_valor_aprovisionado,
                    correct_patronal: selection.data.correct_patronal,
                    diff_patronal_aprovisionado: selection.data.diff_patronal_aprovisionado,
                    correct_base_previdencia: selection.data.correct_base_previdencia,
                    callback: function() {this.reload();}
                }).show();
            }else
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Primeiro selecione o evento a ser editado.',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
        },

        reload: function(){
            var valor = 0;
            var patronal = 0;
            var desconto = 0;
            var status = 1;

            this.getCenterGrid().getStore().reload();
            this.getCenterGrid().getStore().each(
                function(record) {
                    if(record.get('status')[1].alt == 'Provento')
                        valor += record.get('valor');
                    else
                        desconto += record.get('valor');

                    patronal += record.get('patronal');
                    status = record.get('status_folha');
                }
            );

            this.updateStatus(valor, desconto, patronal, (valor - desconto), status);
        },

        showAuditoriaContracheque: function(){
            console.debug('showAuditoriaContracheque...');
            new rh.gfp.lancador.ChangePaychecks({
                folha: this.folha
            }).show();
        },

        recalculate: function() {

            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action('GFPLancador', 'recalculate'),
                params: {
                    payroll: this.folha.pk,
                    // servidor: this.servidor.pk
                },
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
                    }
                    // console.debug(obj);
                },
                failure: function(request) {
                    console.debug(request);
                    alert('Erro processando o recalculo.')
                },
                scope: this
            })
        },

        evaluate: function() {

            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action('GFPPayCheck', 'evaluate'),
                params: {
                    payroll: this.folha.pk,
                    employee: this.servidor.pk
                },
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(!obj.success){
                        Ext.Msg.show({
                            icon: Ext.Msg.ERROR,
                            msg: obj.message,
                            buttons: Ext.Msg.OK
                        });
                    }else{
                        if(obj.message)
                            Ext.Msg.show({
                                icon: Ext.Msg.INFO,
                                msg: obj.message,
                                buttons: Ext.Msg.OK
                            });
                        this.reload();
                    }
                    // console.debug(obj);
                },
                failure: function(request) {
                    console.debug(request);
                    alert('Erro ao avaliar diferenças.')
                },
                scope: this
            })
        },

        remove: function() {
            var selections = this.getCenterGrid().getSelectionModel().getSelections();
            if(selections.length > 0) {
                var fes = [];

                Ext.each(selections, function(fe) {fes.push(fe.get('pk'));});

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPLancador', 'delete'),
                    params: {lancamentos: fes, folha: this.folha.pk, servidor: this.servidor.pk},
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
            else alert('Primeiro selecione os itens a serem removidos.');
        },

        submitMessage: function() {
            var servidor = this.servidor;
            var folha = this.folha;



            new rh.gfp.payroll.PayrollMessageWindow({
                action: (this.servidor.message ? 'update' : 'create'),
                values: 'remote',
                oId: this.servidor.message,
                params: {
                    folha: this.folha.pk,
                    servidor: this.servidor.pk
                },
                callback: {
                    success: {
                        scope: this,
                        fn: function(args) {
                            this.servidor.message = args.pk;
                        }
                    }
                },
                status_callback: this.status_callback,
            }).show();

            // Ext.Ajax.request({
            //     url: toolkit.util.Normalize.controller_action('GFPLancador', 'get_message_from'),
            //     params: {
            //         servidor: this.servidor.pk,
            //         folha: this.folha.pk
            //     },
            //     success: function(request) {
            //         var obj = Ext.decode(request.responseText);
            //         var conf = {}

            //         if(obj.pk) conf = {
            //             type: 'POST',
            //             baseParams: {
            //                 pk: obj.pk,
            //                 folha: this.folha.pk,
            //                 servidor: this.servidor.pk
            //             },
            //             values: {
            //                 texto: obj.texto
            //             }
            //         };
            //         else conf = {
            //             type: 'POST',
            //             baseParams: {
            //                 folha: this.folha.pk,
            //                 servidor: this.servidor.pk
            //             }
            //         }

            //         new toolkit.gfp.FolhaMensage(conf).show();
            //     },
            //     failure: function(request) {

            //     },
            //     scope: this
            // });
        },

        confirmRescission: function() {

            Ext.Msg.show({
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Tem certeza que deseja adicionar os eventos de rescisão?',
                scope: this,
                fn: function(b) {
                    if(b == 'no') return;
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('GFPPayCheck', 'apply_model'),
                        params: {
                            payroll: this.folha.pk,
                            employee: this.servidor.pk,
                            model: 'rescisao'
                        },
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
                            }
                            // console.debug(obj);
                        },
                        failure: function(request) {
                            console.debug(request);
                            alert('Erro processando o cálculo de rescisão.')
                        },
                        scope: this
                    });
                }
            });
        },


        disablePreviewPayslip: function() {
            var selections = this.getTopGrid().getSelectionModel().getSelections();

            if(selections.length > 0) {

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPGestorContracheque', 'disable_preview_payslip'),
                    params: {folha: this.folha.pk, servidor: this.servidor.pk},
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
                        }
                    },
                    failure: function() {
                        Ext.Msg.show({
                            icon: Ext.Msg.ERROR,
                            msg: 'Ocorreu um erro tentando inibir o contracheque.',
                            buttons: Ext.Msg.OK
                        });
                    },
                    scope: this
                });
            }
            else
                Ext.Msg.show({
                    icon: Ext.Msg.ERROR,
                    msg: 'Selecione o contracheque que será inibido ao servidor.',
                    buttons: Ext.Msg.OK
                });
        },


        confirmEvento: function() {
            var selections = this.getCenterGrid().getSelectionModel().getSelections();

            if(selections.length > 0) {
                var params = [];

                Ext.each(
                    selections,
                    function(record) { params.push(record.get('pk')); }
                );

                Ext.Msg.show({
                    icon: Ext.Msg.QUESTION,
                    buttons: Ext.Msg.YESNO,
                    msg: 'Tem certeza que deseja confirmar a validade dos eventos selecionados?',
                    scope: this,
                    fn: function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action('GFPLancador', 'confirm'),
                            params: { fes: params },
                            success: function(request) {
                                var obj = Ext.decode(request.responseText);

                                if(obj.success) {
                                    this.getCenterGrid().getStore().reload();
                                }
                                else alert(obj.message);
                            },
                            failure: function(request) { alert('Ocorreram problemas tentando atender sua solicitação, tente mais tarde novamente.') },
                            scope: this
                        })
                    }
                });
            }
            else alert('Primeiro você deve selecionar os eventos que devem ser confirmados.')
        },

        confirmContraCheque: function() {
            if(this.servidor && this.folha) {
                Ext.Msg.show({
                    icon: Ext.Msg.QUESTION,
                    buttons: Ext.Msg.YESNO,
                    msg: 'Tem certeza que deseja confirmar a validade dos eventos selecionados?',
                    scope: this,
                    fn: function(b) {
                        if(b == 'no') return;

                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action('GFPLancador', 'confirm'),
                            params: {
                                servidor: this.servidor.pk,
                                folha: this.folha.pk
                            },
                            success: function(request) {
                                var obj = Ext.decode(request.responseText);

                                if(obj.success) {
                                    this.getCenterGrid().getStore().reload();
                                }
                                else alert(obj.message);
                            },
                            failure: function(request) { alert('Ocorreram problemas tentando atender sua solicitação, tente mais tarde novamente.') },
                            scope: this
                        })
                    }
                });
            }
            else alert('Primeiro selecione uma folha e um servidor.');
        },

        showPensao: function(type) {
            var Class;

            if(type == 'A')
                Class = toolkit.gfp.PensaoAlimenticiaView;
            else if(type == 'M')
                Class = toolkit.gfp.PensaoMorteView;

            new Class({
                config: {
                    servidor: this.servidor.pk,
                    folha: this.folha.pk
                }
            }).show()
        },

        showDifferences: function() {
            var selection = this.getCenterGrid().getSelectionModel().getSelected();
            if(selection){
                new rh.gfp.lancador.DifferencesWindow({
                    difference: selection.data.paycheck_difference
                }).show()
            }else
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Primeiro selecione um lançamento que seja proveniente de uma diferença automática!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
        },

        associaPensao: function() {
            var selections = this.getCenterGrid().getSelectionModel().getSelections();

            if(selections.length > 0) {
                var params = [];

                Ext.each(
                    selections,
                    function(record) {
                        params.push({
                            'pk': record.get('pk'),
                            'chave': record.get('chave'),
                            'descricao': record.get('descricao'),
                            'valor': record.get('valor')
                        });
                    }
                );

                new toolkit.gfp.PensaoEvento({
                    eventos: params,
                    servidor: this.servidor.pk,
                    folha: this.folha.pk,
                    callback: function() { this.getCenterGrid().getStore().reload(); },
                    scope: this
                }).show()
            }
            else alert('Primeiro você deve selecionar os eventos que devem ser associados.')
        },

        getProxyLancamentos: function(){
            if(!this.proxyLancamentos){
                this.proxyLancamentos = new Ext.data.HttpProxy({
                    scope: this,
                    method: 'POST',
                    api: {
                        read : toolkit.util.Normalize.controller_action('GFPLancador', 'list'),
                        create : toolkit.util.Normalize.controller_action('GFPLancador', 'create'),
                        update: toolkit.util.Normalize.controller_action('GFPLancador', 'update'),
                        destroy: toolkit.util.Normalize.controller_action('GFPLancador', 'destroy'),
                    },
                    listeners:{
                        scope: this,
                        beforewrite: function(proxy, action){
                            console.debug('Before Write Proxy...');
                        },
                        write: function(proxy, action){
                            console.debug('After Write Proxy...');
                            this.reload();
                        },
                    }
                });
            }
            return this.proxyLancamentos;
        },

        getReaderLancamentos: function(){
            if(!this.readerGestorProgressoes){
                this.readerGestorProgressoes = new Ext.data.JsonReader({
                    totalProperty: 'totalRows',
                    successProperty: 'success',
                    idProperty: 'pk',
                    root: 'result',
                    messageProperty: 'message'  // <-- New "messageProperty" meta-data
                }, [
                        {name: 'pk'},
                        {name: 'status'},
                        {name: 'chave'},
                        {name: 'qnt'},
                        {name: 'qnt_desc'},
                        {name: 'qnt_max'},
                        {name: 'pct'},
                        {name: 'parcela'},
                        {name: 'prazo'},
                        {name: 'prazo_desc'},
                        {name: 'descricao'},
                        {name: 'lancamento'},
                        {name: 'tipo'},
                        {name: 'valor'},
                        {name: 'valor_base'},
                        {name: 'patronal'},
                        {name: 'status_folha'},
                        {name: 'info'},
                        {name: 'reference_month'},
                        {name: 'reference_year'},
                        {name: 'evento__pk'},
                        {name: 'evento__automatico'},
                        {name: 'paycheck_difference'},
                        {name: 'paycheck_difference__unicode'},
                        {name: 'base_previdencia'},
                        {name: 'modified_at'},
                        {name: 'modified_by'},
                        {name: 'status_entry'},
                        {name: 'status_entry'},
                        {name: 'correct_valor'},
                        {name: 'diff_valor_aprovisionado'},
                        {name: 'correct_patronal'},
                        {name: 'diff_patronal_aprovisionado'},
                        {name: 'correct_base_previdencia'},
                ]);
            }
            return this.readerGestorProgressoes;
        },

        getWriterLancamentos: function(){
            if(!this.writeLancamentos){
                this.writeLancamentos = new Ext.data.JsonWriter({
                    encode: true,
                    writeAllFields: false
                });
            }
            return this.writeLancamentos;
        },

        getStoreLancamentos: function(){

            if(!this.storeLancamentos){
                this.storeLancamentos = new Ext.data.Store({
                    id: 'store_lancamentos',
                    proxy: this.getProxyLancamentos(),
                    reader: this.getReaderLancamentos(),
                    writer: this.getWriterLancamentos(),  // <-- plug a DataWriter into the store just as you would a Reader
                    autoSave: false, // <-- false would delay executing create, update, destroy requests until specifically told to do so with some [save] buton.
                    listeners: {
                        scope: this,
                        load: function(store) {
                            var valor = 0;
                            var patronal = 0;
                            var desconto = 0;
                            var status = 1;

                            store.each(
                                function(record) {
                                    if(record.get('tipo') == 'PROVENTO')
                                        valor += record.get('valor');
                                    else
                                        desconto += record.get('valor');

                                    patronal += record.get('patronal');
                                    status = record.get('status_folha');
                                }
                            );

                            this.updateStatus(valor, desconto, patronal, (valor - desconto), status);
                        }
                    }
                });
            }
            return this.storeLancamentos;
        },

        getCenterGrid: function() {
            if(!this.centerGrid) {
                this.centerGrid = new Ext.grid.GridPanel({
                    tbar: [
                        this.getActions().adicionar_evento,
                        this.getActions().editar_evento,
                        this.getActions().remover_evento,
                        '-',
                        this.getActions().recalcular_eventos,
                        '-',
                        {
                            iconCls: true,
                            icon: '/' + global.Context + '/static/rh/images/folha-validar.png',
                            text: 'Confirmar',
                            menu: [
                                this.getActions().confirmar_evento,
                                this.getActions().confirmar_contracheque
                            ]
                        },
                        '-',
                        {
                            text: 'Pensões',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/rh/images/folha-pensao.png',
                            tooltip: 'Pessoas que recebem a pensão.',
                            menu: [
                                {
                                    text: 'Pensão Alimenticia',
                                    scope: this,
                                    handler: function() { this.showPensao('A'); }
                                },
                                {
                                    text: 'Pensão por Morte',
                                    scope: this,
                                    handler: function() { this.showPensao('M'); }
                                },
                                '-',
                                {
                                    text: 'Associar debito a beneficiário',
                                    scope: this,
                                    handler: this.associaPensao
                                }
                            ]
                        },
                        '-',
                        {
                            text: 'Dependentes',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/rh/images/folha-dependente.png',
                            tooltip: 'Dependentes do servidor',
                            handler: function() {
                                if(this.servidor && this.folha)
                                    // new toolkit.gfp.GridDependente({
                                    new rh.dependente.DependenteManageWindow({
                                        servidor_id: this.servidor.pk,
                                    }).show();
                                else if(!this.servidor)
                                    alert('Servidor não foi selecionado, primeiro selecione o servidor.');
                                else if(!this.folha)
                                    alert('Primeiro selecione uma folha de pagamento.')
                            },
                            scope: this
                        },
                        '-',
                        {
                            text: 'Mensagem',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/rh/images/folha-mensagem.png',
                            tooltip: 'Mensagem para o contra cheque do servidor.',
                            handler: this.submitMessage,
                            scope: this
                        },
                        '-',
                        this.getActions().rescission,
                        '-',
                        this.getActions().evaluate,
                        this.getActions().differences,
                        '-',
                        this.getDisablePreviewPayslipButton()
                    ],
                    bbar: this.getStatusBar(),
                    style: 'border-top: 1px solid #99BBE8',
                    region: 'center',
                    border: false,
                    store: this.getStoreLancamentos(),
                    autoExpandColumn: 'autoExpand',
                    cm: new Ext.grid.ColumnModel([
                        { header: '', dataIndex: 'status', sortable: true, width: 105, menuDisabled: true, renderer: toolkit.util.formatStatus },
                        {
                            header: 'Evento',
                            dataIndex: 'chave',
                            sortable: true,
                            width: 55,
                            renderer: function(value){
                                if(value.length<5) {
                                    return value;
                                }
                                else{
                                    return value.slice(0,3).concat("-", value.slice(3));
                                }
                            }
                        },
                        { header: 'Descrição', dataIndex: 'descricao', sortable: true, width: 290, id: 'autoExpand'},
                        { header: "Mês/Ano Ref.", width: 80, dataIndex: 'reference', renderer: function(value, p, r){
                            var zero = r.data['reference_month'] < 10 ? '0' : '';
                            return zero + r.data['reference_month'] + "/" + r.data['reference_year'];
                        }, menuDisabled: true},
                        { header: 'Quantidade', dataIndex: 'qnt_desc', width: 80, menuDisabled: true },
                        { header: 'Percentual', dataIndex: 'pct', width: 70, menuDisabled: true },
                        { header: 'Prazo', dataIndex: 'prazo_desc', width: 120, menuDisabled: true },
                        { header: 'Valor (R$)', dataIndex: 'valor', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true},
                        { header: 'Valor Devido (R$)', dataIndex: 'correct_valor', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true},
                        { header: 'Valor Base (R$)', dataIndex: 'valor_base', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true },
                        { header: 'Patronal (R$)', dataIndex: 'patronal', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true},
                        { header: 'Patronal Devido (R$)', dataIndex: 'correct_patronal', width: 90, renderer: toolkit.util.formatCurrency, menuDisabled: true}
                    ]),
                    sm: new Ext.grid.RowSelectionModel({
                        singleSelection: true,
                        listeners: {
                            rowselect: function(row) {
//                                 console.debug('ROWSELECT...');
                                fe = row.getSelected().json
                                this.getAuditTextItem().setText(fe.modified_by+' '+fe.modified_at);
                            },
                            scope: this
                        }
                    }),
                    viewConfig: {
                        stripeRows: false,
                        getRowClass: function(record, index, rowParams, store){
//                             console.debug(record);
                            style = (record.data.tipo == 'PROVENTO'? 'prov-entry': 'desc-entry');
                            style += (record.data.status_entry == 'NC'? ' nc-entry': '');
                            return style;
                        }
                    },
                    listeners: {
                        scope: this,
                        dblclick: this.editEvento,
                        render: function(p) {
                            new Ext.LoadMask(
                                p.getEl(),
                                {
                                    msg: 'Corregando os lançamentos...',
                                    store: p.getStore()
                                }
                            );
                        },
                        contextmenu: function(event) {
                            var menu = new Ext.menu.Menu({
                                items: [
                                    this.getActions().remover_evento,
                                    {
                                        text: 'Confirmar',
                                        icon: '/' + global.Context + '/static/rh/images/folha-validar.png',
                                        menu: [
                                            this.getActions().confirmar_evento,
                                            this.getActions().confirmar_contracheque
                                        ]
                                    }
                                ]
                            });

                            menu.showAt([event.browserEvent.clientX, event.browserEvent.clientY]);

                            event.stopEvent();
                        },
                    }
                });
            }
            return this.centerGrid
        },

        setServidor: function(servidor) {
            this.servidor = servidor;
            this.getActions().servidor_contracheque.setText('<font style="color: #15428B; "><b>'+this.servidor.matricula + ' - '+this.servidor.nome+'</b></font>');
            this.refreshContraCheque();
        },

        unsetServidor: function() {
            this.servidor = null;
            this.getActions().servidor_contracheque.setText('');
            this.getTopGrid().getSelectionModel().clearSelections();
            this.refreshContraCheque();
        },

        selectFirstServidor: function(){
            this.getTopGrid().getSelectionModel().selectFirstRow();
        },

        setFolha: function(folha) {
            this.folha = folha;
            var store = this.getTopGrid().getStore();
            store.setBaseParam('folha', this.folha.pk);
            store.load({});
            this.unsetServidor();
        },

        changeStatusFolha: function(statusType) {
            var msg = false;

            if(statusType == 3)
                msg = 'Primeiro cheque se existem pendencias para esta folha, pois, ' +
                      'todas as pendencias de validação da folha ' + this.folha.description + ' serão aprovados por você.</br></br>' +
                      'Tem certeza que deseja mudar o status da folha de pagamento para fechado?';
            else
                msg = 'Tem certeza que deseja mudar o status da folha ' + this.folha.description + '?';

            Ext.Msg.show({
                title: 'Status da Folha de Pagamento',
                msg: msg,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                fn: function(b) {

                    if(b == 'no') return;

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'GFPLancador',
                            'update_status_folha'
                        ),
                        params: {
                            pk: this.folha.pk,
                            status: statusType
                        },
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);

                            if(obj.success){
                                this.folha = obj.folha;
                                this.refreshContraCheque();
                            }
                            else alert(obj.message);
                        },
                        scope: this
                    })
                },
                scope: this
            });
        },

        getActions: function(){
            if(!this.actions){
                this.actions = {};
                this.actions.novo_contracheque= new Ext.Action({
                    text: 'Novo',
                    icon: '/' + global.Context + '/static/images/add.png',
                    iconCls: true,
                    tooltip: 'Novo Contracheque',
                    scope: this,
                    handler: this.addContracheque,
                    // disabled: true
                });
                this.actions.apagar_contracheque= new Ext.Action({
                    text: 'Apagar',
                    icon: '/' + global.Context + '/static/images/delete.png',
                    iconCls: true,
                    tooltip: 'Apagar Contracheque',
                    scope: this,
                    handler: this.removeContracheque,
                    // disabled: true
                });
                this.actions.list_changes= new Ext.Action({
                    text: 'Alterações',
                    icon: '/' + global.Context + '/static/rh/images/ferias_conflito.png',
                    iconCls: true,
                    tooltip: 'Alterações nos contracheques',
                    scope: this,
                    handler: this.showAuditoriaContracheque,
                    // disabled: true
                });
                this.actions.adicionar_evento= new Ext.Action({
                    text: 'Adicionar',
                    icon: '/' + global.Context + '/static/images/add.png',
                    iconCls: true,
                    tooltip: 'Adicionar Evento',
                    scope: this,
                    handler: this.addEvento,
                    disabled: true
                });
                this.actions.remover_evento= new Ext.Action({
                    text: 'Remover',
                    icon: '/' + global.Context + '/static/images/delete.png',
                    iconCls: true,
                    tooltip: 'Remover Evento',
                    scope: this,
                    handler: this.remove,
                    disabled: true
                });
                this.actions.editar_evento= new Ext.Action({
                    text: 'Editar',
                    icon: '/' + global.Context + '/static/images/edit.png',
                    iconCls: true,
                    tooltip: 'Editar Evento',
                    scope: this,
                    handler: this.editEvento,
                    disabled: true
                });
                this.actions.recalcular_eventos= new Ext.Action({
                    text: 'Recalcular',
                    icon: '/' + global.Context + '/static/rh/images/folha-recalcular.png',
                    iconCls: true,
                    tooltip: 'Recalcular folha',
                    scope: this,
                    handler: this.recalculate,
                    disabled: true
                });
                this.actions.confirmar_evento= new Ext.Action({
                    text: 'Evento',
                    // icon: '/' + global.Context + '/static/rh/images/folha-recalcular.png',
                    // iconCls: true,
                    tooltip: 'Confirmar Evento',
                    scope: this,
                    handler: this.confirmEvento,
                    disabled: true
                });
                this.actions.confirmar_contracheque= new Ext.Action({
                    text: 'Contracheque',
                    // icon: '/' + global.Context + '/static/rh/images/folha-recalcular.png',
                    // iconCls: true,
                    tooltip: 'Confirmar Contracheque',
                    scope: this,
                    handler: this.confirmContraCheque,
                    disabled: true
                });
                this.actions.rescission= new Ext.Action({
                    text: 'Aplicar modelo',
                    icon: '/' + global.Context + '/static/rh/images/down.png',
                    iconCls: true,
                    scope: this,
                    menu: [
                        {
                            text: 'Rescisão',
                            scope: this,
                            handler: this.confirmRescission
                        }
                    ]
                });
                this.actions.servidor_contracheque= new Ext.Action({
                    text: '',
                    handler: function(){},
                    // iconCls: 'icon-core icon-core-run',
                    itemId: 'servidorContracheque',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    // disabled: true,
                    scope: this
                });
                this.actions.folha= new Ext.Action({
                    text: '---',
                    handler: this.selectPeriod,
                    iconCls: 'icon-core icon-core-run',
                    itemId: 'folhaTrabalho',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    // disabled: true,
                    scope: this
                });
                this.actions.auditoria= new Ext.Action({
                    text: '---',
                    handler: function(){},
                    // iconCls: 'icon-core icon-core-run',
                    itemId: 'auditoria',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    // disabled: true,
                    scope: this
                });
                this.actions.evaluate = new Ext.Action({
                    text: 'Avaliar Diferenças',
                    handler: this.evaluate,
                    iconCls: 'icon-fopag icon-task-select',
                    itemId: 'evaluate',
                    // style: {
                    //     'color': '#FF0000',
                    //     'font-weight': 'bold'
                    // },
                    // disabled: true,
                    scope: this
                });
                this.actions.differences = new Ext.Action({
                    text: 'Diferenças',
                    handler: this.showDifferences,
                    iconCls: 'icon-fopag icon-task-select',
                    itemId: 'differences',
                    // style: {
                    //     'color': '#FF0000',
                    //     'font-weight': 'bold'
                    // },
                    // disabled: true,
                    scope: this
                });
                this.actions.folha_anterior= new Ext.Action({
                    text: '',
                    handler: this.prevPeriod,
                    icon: '/' + global.Context + '/static/js/ext/resources/images/default/grid/page-prev.gif',
//                     iconCls: true,
                    iconCls: true,
                    itemId: 'folha_anterior',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    tooltip: 'Anterior',
                    // disabled: true,
                    scope: this
                });this.actions.folha_posterior= new Ext.Action({
                    text: '',
                    handler: this.nextPeriod,
                    icon: '/' + global.Context + '/static/js/ext/resources/images/default/grid/page-next.gif',
//                     iconCls: true,
                    iconCls: true,
                    itemId: 'folha_posterior',
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    },
                    tooltip: 'Próxima',
                    // disabled: true,
                    scope: this
                });
            }
            return this.actions;
        },

        getServidorButton: function() {
            if(!this.servidorButton){
                this.servidorButton= new Ext.Button(this.getActions().servidor_contracheque);
            }
            return this.servidorButton;
        },

        getDisablePreviewPayslipButton: function() {
            if(!this._disablePreviewPayslipButton){
                this._disablePreviewPayslipButton = new Ext.Button({
                    text: 'Inibir Contracheque',
                    scope: this,
                    icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                    iconCls: true,
                    tooltip: 'habilitar/desabilitar a visualização do contracheque pelo servidor',
                    handler: this.disablePreviewPayslip,
                    enableToggle: true,
                });
            }
            return this._disablePreviewPayslipButton;
        },


        getAuditTextItem: function(){
            if(!this.auditText){
                this.auditText= new Ext.Toolbar.TextItem({
                    text: '---',
                    style: {
                        // 'color': '#FF0000',
                        'font-weight': 'bold'
                    }
                });
            }
            return this.auditText;
        },
        getProventosTextItem: function(){
            if(!this.proventosText){
                this.proventosText= new Ext.Toolbar.TextItem({
                    text: 'Proventos: R$ 0,00',
                    width: 135,
                    style: {
                        'color': '#15428B',
                        'font-weight': 'bold'
                    }
                });
            }
            return this.proventosText;
        },
        getDescontosTextItem: function(){
            if(!this.descontosText){
                this.descontosText= new Ext.Toolbar.TextItem({
                    text: 'Descontos: R$ 0,00',
                    width: 135,
                    style: {
                        'color': '#FF0000',
                        'font-weight': 'bold'
                    }
                });
            }
            return this.descontosText;
        },
        getLiquidoTextItem: function(){
            if(!this.liquidoText){
                this.liquidoText= new Ext.Toolbar.TextItem({
                    text: 'Líquido: R$ 0,00',
                    width: 135,
                    style: {
                        'color': '#14950E',
                        'font-weight': 'bold'
                    }
                });
            }
            return this.liquidoText;
        },
        getPatronalTextItem: function(){
            if(!this.patronalText){
                this.patronalText= new Ext.Toolbar.TextItem({
                    text: 'Patronal: R$ 0,00',
                    width: 135,
                    style: {
                        // 'color': '#FF0000',
                        'font-weight': 'bold'
                    }
                });
            }
            return this.patronalText;
        },

        updatePayRoll: function(){

        },

        upatePayCheck: function(){

        },

        onSelectEvent: function(){

        },

        updateStatus: function(proventos, descontos, patronal, liquido) {
            var st = this.getStatusBar();
            // var sbutton = this.getStatusButton();
            // var actStatus = this.getActions().status_folha;
            // var btStatusFolha = this.getStatusButton();
            var actFolha = this.getActions().folha;

            status = this.folha.status;
            switch(status){
                case "1":
                    // actStatus.setIconClass('icon-core icon-core-run');
                    actFolha.setIconClass('icon-core icon-core-run');
                    // btStatusFolha.setTooltip('Folha em Produção');
                    break;
                case "2":
                    // actStatus.setIconClass('icon-core icon-core-waiting');
                    actFolha.setIconClass('icon-core icon-core-waiting');
                    // btStatusFolha.setTooltip('Folha em Análise');
                    break;
                case "3":
                    // actStatus.setIconClass('icon-fopag icon-closed-padlock');
                    actFolha.setIconClass('icon-fopag icon-closed-padlock');
                    // btStatusFolha.setTooltip('Folha Fechada');
                    break;
                case "4":
                    // actStatus.setIconClass('icon-fopag icon-stamp-arrow');
                    actFolha.setIconClass('icon-fopag icon-stamp-arrow');
                    // btStatusFolha.setTooltip('Folha Processada');
                    break;
                default:
                    console.debug('ERRO: status da folha indefinido!');

            }
            actFolha.setText('<font style="color: #FF0000; "><b>'+this.folha.unicode+'</b></font>');
            // this.getAuditTextItem().setText('user dd-mm-aaaa hh:mm');
            this.getProventosTextItem().setText('Proventos: R$ ' + Ext.util.Format.number(proventos ? proventos : 0.0, '0.0,00/i'));
            this.getDescontosTextItem().setText('Descontos: ' + Ext.util.Format.number(descontos ? descontos : 0.0, '0.0,00/i'));
            this.getLiquidoTextItem().setText('Liquido: R$ ' + Ext.util.Format.number(liquido ? liquido : 0.0, '0.0,00/i'));
            this.getPatronalTextItem().setText('Patronal: R$ ' + Ext.util.Format.number(patronal ? patronal : 0.0, '0.0,00/i'));
            // var items = [
            //     [
            //         this.getAuditTextItem(),
            //         '->',
            //         '-',
            //         'Proventos: R$ ' + Ext.util.Format.number(proventos ? proventos : 0.0, '0.0,00/i'),
            //         '-',
            //         'Descontos: ' + Ext.util.Format.number(descontos ? descontos : 0.0, '0.0,00/i'),
            //         '-',
            //         'Patronal: R$ ' + Ext.util.Format.number(patronal ? patronal : 0.0, '0.0,00/i'),
            //         '-',
            //         'Liquido: R$ ' + Ext.util.Format.number(liquido ? liquido : 0.0, '0.0,00/i')
            //     ]
            // ];

            // st.removeAll();
            // st.add(items);
        },

        refreshContraCheque: function() {
            var store = this.getCenterGrid().getStore();
            var actions = this.getActions();
            if(this.servidor && this.folha){
                store.baseParams = {
                    'servidor': this.servidor.pk,
                    'folha': this.folha.pk
                };
                this.previewPayslipButton(store);
                store.load({});
                if(this.folha.status!= 3){
                    actions.adicionar_evento.setDisabled(false);
                    actions.editar_evento.setDisabled(false);
                    actions.remover_evento.setDisabled(false);
                    actions.recalcular_eventos.setDisabled(false);
                    actions.confirmar_contracheque.setDisabled(false);
                    actions.confirmar_evento.setDisabled(false);
                }

            }else{
                store.baseParams = {};
                store.removeAll();
                this.updateStatus();
                // actions.adicionar_evento.setDisabled(true);
                actions.editar_evento.setDisabled(true);
                // actions.remover_evento.setDisabled(true);
                actions.recalcular_eventos.setDisabled(true);
                actions.confirmar_contracheque.setDisabled(true);
                actions.confirmar_evento.setDisabled(true);
            }

        },

        previewPayslipButton: function(value) {
            if(value) {
                this.getStatusPayslip(value.baseParams);
            }
        },

        getStatusPayslip: function(values) {
            var scope = this;
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action('GFPGestorContracheque', 'get_status_payslip'),
                params: { servidor: values.servidor, folha: values.folha},
                success: function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.hasPayslip){
                        this.getDisablePreviewPayslipButton().enable();
                        if(obj.blocked) {
                            this.getDisablePreviewPayslipButton().toggle(true, true);
                        } else {
                            this.getDisablePreviewPayslipButton().toggle(false, true);
                        }
                    } else {
                        this.getDisablePreviewPayslipButton().toggle(false);
                        this.getDisablePreviewPayslipButton().disable();
                    }
                },
                failure: function() {
                    Ext.MessageBox.show({
                       title: 'Erro',
                       msg: 'Ocorreu um erro inesperado',
                       buttons: Ext.MessageBox.OK,
                       icon: Ext.MessageBox.ERROR
                    })
                },
                scope: this
            });

        },

        selectPeriod: function() {
            var scope = this;
            new toolkit.gfp.SelecionaFolha(
                function(folha){scope.setFolha(folha);},
                {folha: this.folha}
            ).show();
        },

        toggleOnlyActive: function() {
            this.onlyActive = (this.onlyActive != true);
            this.getTopGrid().getStore().baseParams['onlyActive'] = this.onlyActive;
            this.getTopGrid().getStore().load({});
        },

        toggleOnlyServidorFolha: function() {
            this.onlyServidorFolha = !this.getTopGrid().getStore().baseParams['onlyServidorFolha'];
            console.debug(this.onlyServidorFolha);
            this.getTopGrid().getStore().baseParams['onlyServidorFolha'] = this.onlyServidorFolha;
            this.getTopGrid().getStore().load({});
        },

        toggleOnlyContrachequeNegativos: function() {
            this.onlyNegatives = (this.onlyNegatives != true);
            this.getTopGrid().getStore().baseParams['onlyNegatives'] = this.onlyNegatives;
            this.getTopGrid().getStore().load({});
        },

        toggleOnlyTipoServidor: function(menuItem) {
            if(menuItem.value=='') delete(this.getTopGrid().getStore().baseParams.onlyTipoServidor);
            else this.getTopGrid().getStore().baseParams['onlyTipoServidor'] = menuItem.value;
            this.getTopGrid().getStore().load({});
        },

        toggleOnlyPensao: function(conf) {
            var store = this.getTopGrid().getStore();

            if(conf.alimenticia) {
                this.onlyPensaoAlimenticia = (this.onlyPensaoAlimenticia != true)
                store.baseParams['onlyPensaoAlimenticia'] = this.onlyPensaoAlimenticia;
            }

            if(conf.morte) {
                this.onlyPensaoMorte = (this.onlyPensaoMorte != true);
                store.baseParams['onlyPensaoMorte'] = this.onlyPensaoMorte
            }

            store.load({});
        },

        getTopGrid: function() {
            if(!this.topGrid) {
                this.textSearch = new Ext.form.TextField({
                    emptyText: 'Buscar por matrícula ou nome.',
                    width: 350,
                    enableKeyEvents: true
                });

                var label = new Ext.form.Label({
                    text: 'Buscar : ',
                    forId: this.textSearch.getId()
                });

                var store = new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action(
                        'GFPLancador',
                        'get_servidor_list'
                    ),
                    root: 'result',
                    autoLoad: false,
                    totalProperty: 'count',
                    fields: ['pk', 'nome', 'matricula', 'cargo', 'funcao', 'status', 'estagiario', 'referencia_ferias', 'modified_at', 'modified_by'],
                    baseParams: {
                        limit: 50,
                        start: 0,
                        onlyServidorFolha: true,
                        onlyMembro: this.onlyMembro,
                        onlyAdministrativo: this.onlyAdministrativo
                    },
                    listeners: {
                        load: function( st, records, options ){
                            // console.debug('LOADING SERVIDORES...');
                            this.unsetServidor();
                            this.selectFirstServidor();
                        },
                        scope: this
                    }
                });

                this.textSearch.on(
                    'change',
                    function(obj, newValue) {
                        store.baseParams['start'] = 0;
                        store.baseParams['query'] = newValue;
                    }
                );

                this.textSearch.on(
                    'keypress',
                    function(obj, event) {
                        if(event.getKey() == Ext.EventObject.ENTER) {
                            store.baseParams['start'] = 0;
                            store.baseParams['query'] = obj.getValue();
                            store.load({});
                        }
                    }
                );

                this.topGrid = new Ext.grid.GridPanel({
                    tbar: [
                        this.getActions().novo_contracheque,
                        this.getActions().apagar_contracheque,
                        '-',
                        this.getActions().list_changes,
                        // {
                            // text: 'Novo',
                            // handler: this.selectPeriod,
                            // scope: this,
                            // iconCls: true,
                            // icon: '/' + global.Context + '/static/rh/images/fixo.png'
                        // },{
                        //     text: 'Apagar',
                        //     handler: this.selectPeriod,
                        //     scope: this,
                        //     iconCls: true,
                        //     icon: '/' + global.Context + '/static/rh/images/fixo.png'
                        // },
                        '-',
                        label,
                        ' ',
                        ' ',
                        this.textSearch,
                        ' ',
                        {
                            iconCls: true,
                            icon: '/' + global.Context + '/static/images/clean.png',
                            handler: function() {this.textSearch.setValue('');store.baseParams['query'] = ''},
                            scope: this
                        },
                        ' ',
                        '-',
                        {
                            text: 'Filtro',
                            iconCls: true,
                            icon: '/' + global.Context + '/static/rh/images/conf-filtro.png',
                            menu: [
                                {
                                    text: 'Servidores da Folha',
                                    iconCls: true,
                                    checked: true,
                                    scope: this,
                                    handler: this.toggleOnlyServidorFolha,
                                    enableToggle: true,
                                    listeners:{
                                        toggle: function(btn, pressed){
                                            console.debug(pressed);
                                        }
                                    }
                                },
                                {
                                    text: 'Ativo',
                                    iconCls: true,
                                    checked: false,
                                    scope: this,
                                    handler: this.toggleOnlyActive
                                },
                                '-',
                                {
                                    text: 'Contracheque negativos',
                                    iconCls: true,
                                    checked: false,
                                    scope: this,
                                    handler: this.toggleOnlyContrachequeNegativos
                                },
                                '-',
                                {
                                    text: 'Todos',
                                    group: 'tipoServidor',
                                    value: '',
                                    checked: true,
                                    scope: this,
                                    handler: this.toggleOnlyTipoServidor
                                },{
                                    text: 'Estagiários',
                                    group: 'tipoServidor',
                                    value: 'E',
                                    checked: false,
                                    scope: this,
                                    handler: this.toggleOnlyTipoServidor
                                },{
                                    text: 'Administrativos',
                                    group: 'tipoServidor',
                                    value: 'S',
                                    checked: false,
                                    scope: this,
                                    handler: this.toggleOnlyTipoServidor
                                },{
                                    text: 'Membros',
                                    group: 'tipoServidor',
                                    value: 'M',
                                    checked: false,
                                    scope: this,
                                    handler: this.toggleOnlyTipoServidor
                                },
                                '-',
                                {
                                    text: 'Pensão Alimenticia',
                                    checked: false,
                                    scope: this,
                                    handler: function() {this.toggleOnlyPensao({alimenticia:true, morte: false}) }
                                },
                                {
                                    text: 'Pensão por Morte',
                                    checked: false,
                                    scope: this,
                                    handler: function() {this.toggleOnlyPensao({alimenticia:false, morte: true}) }
                                }
                            ]
                        }
                    ],
                    region: 'north',
                    border: false,
                    minHeight: 235,
                    maxHeight: 295,
                    height: 235,
                    split: true,
                    style: 'border-bottom: 1px solid #99BBE8',
                    store: store,
                    bbar: new Ext.PagingToolbar({
                        store: store,
                        displayInfo: true,
                        pageSize: 50,
                        items: [
                            '-',
                            // this.getStatusButton(),
                            new Ext.Button(this.getActions().folha_anterior),
                            new Ext.Button(this.getActions().folha),
                            new Ext.Button(this.getActions().folha_posterior),
                            '-',
                            this.getServidorButton(),// Ext.Button(this.getActions().servidor_contracheque),
                        ]
                    }),
                    sm: new Ext.grid.RowSelectionModel({
                        singleSelection: true,
                        listeners: {
                            rowselect: function(row) {
                                cc = row.getSelected().json
                                this.setServidor(cc);
                                this.getAuditTextItem().setText(cc.modified_by+' '+cc.modified_at);
                            },
                            scope: this
                        }
                    }),
                    autoExpandColumn: 'autoExpand',
                    cm: new Ext.grid.ColumnModel([
                        {
                            // id: 'status',
                            header: '',
                            dataIndex: 'status',
                            width: 95,
                            menuDisabled: true,
                            renderer: core.rendererIconGrid
                        },
                        {
                            dataIndex: 'matricula',
                            header: 'Matricula',
                            sortable: true,
                            width: 80,
                            renderer: function(value) {return '<p style="text-align:right">' + value + "</p>";}
                        },
                        {
                            dataIndex: 'nome',
                            header: 'Nome',
                            sortable: true,
                            width: 390,
                            id: 'autoExpand'
                        },
                        {
                            dataIndex: 'cargo',
                            header: 'Efetivo',
                            sortable: true,
                            width: 100,
                            menuDisbaled: true
                        },
                        {
                            dataIndex: 'funcao',
                            header: 'Confiança',
                            sortable: true,
                            width: 70,
                            menuDisabled: true
                        },
                        {
                            dataIndex: 'estagiario',
                            header: 'Estagio',
                            width: 50,
                            menuDisabled: true
                        },
                        {
                            dataIndex: 'referencia_ferias',
                            header: 'Ref. de Férias',
                            width: 90,
                            menuDisabled: true
                        }
                    ])
                });

                this.topGrid.on({
                    render: function(p) {
                        new Ext.LoadMask(
                            p.getEl(),
                            {
                                msg: 'Corregando a relação de servidores...',
                                store: p.getStore()
                            }
                        );
                    }
                });
            }

            return this.topGrid;
        },

        prevPeriod: function() {
            var scope = this;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPPayroll', 'select'),
                    params: { payroll: this.folha.pk, direction: 'previous'},
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(!obj.success) {
                            Ext.MessageBox.show({
                               title: 'Erro',
                               msg: obj.message,
                               buttons: Ext.MessageBox.OK,
                               icon: Ext.MessageBox.ERROR
                            })
                        } else {
                            scope.setFolha(obj.payroll);
                        }
                    },
                    failure: function() {
                        Ext.MessageBox.show({
                           title: 'Erro',
                           msg: 'Ocorreu um erro inesperado',
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        })
                    },
                    scope: this
                });

        },

        nextPeriod: function() {
            var scope = this;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPPayroll', 'select'),
                    params: { payroll: this.folha.pk, direction: 'next'},
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(!obj.success) {
                            Ext.MessageBox.show({
                               title: 'Erro',
                               msg: obj.message,
                               buttons: Ext.MessageBox.OK,
                               icon: Ext.MessageBox.ERROR
                            })
                        } else {
                            scope.setFolha(obj.payroll);
                        }

                    },
                    failure: function(response, opts) {
                        Ext.MessageBox.show({
                           title: 'Erro',
                           msg: 'Ocorreu um erro inesperado',
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        })
                    },
                    scope: this
                });

        },

        constructor: function() {
            var cf = {
                title: 'Lançador de Eventos',
                closable: true,
                layout: 'border',
                items: [
                    this.getTopGrid(),
                    this.getCenterGrid()
                ],
                autoScroll: false,
                onlyMembro: true,
                onlyAdministrativo: true
            };

            rh.gfp.lancador.Lancador.superclass.constructor.call(this, cf);

            var ts = toolkit.Application.tabspace;

            ts.remove(ts.getActiveTab());
            ts.add(this);
            ts.setActiveTab(this);

            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'GFPPayroll',
                    'working'
                ),
                method: 'POST',
                success: function(request) {
                    //Type name of new folder
                    var code = Ext.decode(request.responseText);
                    this.setFolha(code.payroll);
                },
                scope: this
            });
        }
    }
);
