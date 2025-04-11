
Ext.ns('toolkit.rh.gestorafastamento.utils');

Ext.apply(toolkit.rh.gestorafastamento.utils,{

    SubstituicaoGridPanel: Ext.extend(toolkit.rh.utils.CustomGridPanel,{
        constructor: function(args) {
            // console.debug('SubstituicaoGridPanel');
            this.afastamento = args.afastamento;
            this.servidor = args.servidor;
            this.servidor_tipo = args.servidor_tipo;
            var cf = args;
            cf.title = (cf.title == undefined ? 'Substituições' : cf.title);
            cf.height = (cf.height == undefined ? 232 : cf.height);
            cf.searchable = (cf.searchable == undefined ? true : cf.searchable);
            cf.border = (cf.border == undefined ? false : cf.border);
            cf.controller = (cf.controller == undefined ? 'RHMovimentacaoSubstituicaoMembro' : cf.controller);
            cf.pageSize = (cf.pageSize == undefined ? 5 : cf.pageSize);
            cf.readerFields = (cf.readerFields == undefined ? ([
                    {name: 'pk'},{name: 'data_inicio'},{name: 'data_fim'},
                    {name: 'substituto'},{name: 'cargo'},{name: 'situacao'},
                    {name: 'tipo'}, {name: 'data_prevista'}, {name: 'pendencia'}
                ]) : cf.readerFields);
            cf.listeners = (cf.listeners == undefined ? {
                    scope: this,
                    dblclick: function() {
                        this.servidor_tipo = this.getSelectionModel().getSelected().get('tipo');
                        this.callWindowFormSubstituicao(
                            'EDIT',
                            this.getSelectionModel().getSelected().get('pk')
                        );
                    },
                    beforeshow: function(component){ this.getStore().load(); }
                } : cf.listeners);
            toolkit.rh.gestorafastamento.utils.SubstituicaoGridPanel.superclass.constructor.call(this, cf);
        },

        callWindowFormSubstituicao: function(tipo_form, substituicao){
            if(tipo_form == 'EDIT' && substituicao == undefined){
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Selecione uma substituição!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
                return;
            }
            if(this.servidor_tipo == 'membro'){
                new toolkit.rh.gestorafastamento.utils.WindowFormSubstituicaoMembro({
                    'substituicao': substituicao,
                    'afastamento': this.afastamento,
                    'servidor': this.servidor,
                    'store_call_back': this.getStore()}).show();
            }else if(this.servidor_tipo == 'servidor'){
                new toolkit.rh.gestorafastamento.utils.ExtCrudCall({
                    pk: substituicao,
                    tipo: tipo_form,
                    controller: 'RHMovimentacaoSubstituicao',
                    store: this.getStore(),
                    fields: [{
                        name: 'afastamento',
                        enabled: false,
                        value: this.afastamento
                    }]
                }).call();
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Impossível identificar esta substituição!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
                return;
            }
        },

        getStore: function(){
            var store = toolkit.rh.gestorafastamento.utils.SubstituicaoGridPanel.superclass.getStore.call(this, {});
            store.baseParams.servidor = this.servidor;
            store.baseParams.afastamento = this.afastamento;
            return store;
        },

        getColumnModel: function(){
            if(!this.colModelGridPanel){
                this.colModelGridPanel = new Ext.grid.ColumnModel({
                    columns: [
                        {
                            dataIndex: 'pendencia',
                            key: 'pendencia',
                            id: 'pendencia',
                            width: 20,
                            renderer: function(value){
                                var tpl = new Ext.XTemplate(
                                    "<div>",
                                        "<tpl for=\"icons\">",
                                        "<img style=\"margin-right:4px;width:12px;height:12px;)\" src=\"{url}\" title=\"{title}\"/>",
                                        "</tpl>",
                                    "</div>"
                                );
                                return tpl.apply({
                                    'icons': {
                                        url: toolkit.util.Normalize.controller_action(
                                            'static/engine/images', 'icons') + (
                                                value.conflito == true ? 'athenas-0024.png' : 'athenas-0073.png'),
                                        title: value.title
                                    }
                                });
                            }
                        },
                        {header: 'Código', sortable: false, dataIndex: 'pk', key: 'pk', id: 'pk', width: 50},
                        {header: 'Cargo', sortable: false, dataIndex: 'cargo', key: 'cargo', id: 'cargo', width: 163},
                        {header: 'Substituto', sortable: false, dataIndex: 'substituto', key: 'substituto', id: 'substituto', width: 184},
                        {header: 'Situação', sortable: true, dataIndex: 'situacao', key: 'situacao', width: 60},
                        {header: 'Início', sortable: true, dataIndex: 'data_inicio', key: 'data_inicio', width: 70},
                        {header: 'Prevista', sortable: true, dataIndex: 'data_prevista', key: 'data_prevista', width: 70},
                        {header: 'Fim', sortable: true, dataIndex: 'data_fim', key: 'data_fim', width: 70}
                    ]
                });
            }
            return this.colModelGridPanel;
        },

        getToolbar: function(){
            var tbar = toolkit.rh.gestorafastamento.utils.SubstituicaoGridPanel.superclass.getToolbar.call(this, {});
            tbar.insertButton(1, {
                    iconCls: true,
                    icon: '/' + global.Context + '/static/images/add.png',
                    handler: function() {
                        this.callWindowFormSubstituicao(
                            'NEW',
                            undefined
                        );
                    },
                    scope: this
                });
            tbar.insertButton(2, '-');
            tbar.insertButton(3, {
                    iconCls: true,
                    icon: '/' + global.Context + '/static/images/edit.png',
                    handler: function() {
                        this.callWindowFormSubstituicao(
                            'EDIT',
                            this.getSelectionModel().getSelected().get('pk')
                        );
                    },
                    scope: this
                });
            tbar.insertButton(4, '-');
            tbar.insertButton(5, {
                    iconCls: true,
                    icon: '/' + global.Context + '/static/images/delete.png',
                    handler: function() {
                        if(this.getSelectionModel().getSelected()){
                            var id = this.getSelectionModel().getSelected().get('pk');
                            var fn = function(bnt, text, opts) {

                                if(bnt == 'yes') {
                                    var obj = toolkit.util.Ajax.request_json(
                                        'POST',
                                        toolkit.util.Normalize.controller_action(
                                            this.getSelectionModel().getSelected().get('tipo') == 'servidor' ? 'RHMovimentacaoSubstituicao' : 'RHMovimentacaoSubstituicaoMembro',
                                            'commit',
                                            ['DELETE', id, 0])
                                    );
                                    var store = this.getStore();
                                    setTimeout(function() { store.load(); }, 100);
                                }
                                else if(bnt == 'no') {
                                    if(this.getSelectionModel().getSelected().get('tipo') == 'servidor'){
                                        this.chamarExtCrud({
                                            controller: 'RHMovimentacaoSubstituicao',
                                            pk: this.getSelectionModel().getSelected().get('pk'),
                                            tipo: 'DELETE',
                                            fields: [{ name: 'servidor', enabled: false }]
                                        });
                                    }else{
                                        new toolkit.rh.gestorafastamento.utils.WindowFormSubstituicaoMembro({
                                            'substituicao': this.getSelectionModel().getSelected().get('pk'),
                                            'afastamento': undefined,
                                            'servidor': undefined,
                                            'store_call_back': this.getStore()
                                        }).show();
                                    }
                                }
                                else {
                                    Ext.MessageBox.show({
                                        title: 'Sistema Administrativo',
                                        msg : 'A ação de remoção foi cancelada.',
                                        buttons: Ext.MessageBox.OK,
                                        icon: Ext.MessageBox.INFO
                                    });
                                }

                            }

                            Ext.MessageBox.show({
                                title: 'ManagerNetWork',
                                msg : 'Tem certeza que deseja remover o item com id ' + id + ', \n\
                                    caso não tenha certeza clique em <b>Não</b> para visualizar os dados. \n\
                                    <b>TODAS substituições</b> agendadas para este afastamento serão apagadas!',
                                fn : fn,
                                scope: this,
                                buttons: Ext.MessageBox.YESNOCANCEL,
                                icon: Ext.MessageBox.QUESTION
                            });
                        }else{ alert('Escolha uma Substituição!');}
                    },
                    scope: this
                });
            tbar.insertButton(6, '-');
            return tbar;
        }
    }),

    WindowFormSubstituicaoMembro: Ext.extend( Ext.Window,{
        constructor: function(args) {
            this.substituicao = args.substituicao ? args.substituicao : undefined;
            this.data_substituicao = this.getData(this.substituicao);
            this.afastamento = args.afastamento ? args.afastamento : undefined;
            this.servidor = args.servidor ? args.servidor : undefined;
            this.store_call_back = args.store_call_back ? args.store_call_back: undefined;
            var cf = {
                title: 'Substituição de Membros',
                closable: true,
                resizable: false,
                modal: true,
                border: false,
                width: 530,
                autoHeight: true,
                items:[ this.getForm() ]
            };
            toolkit.rh.gestorafastamento.utils.WindowFormSubstituicaoMembro.superclass.constructor.call(this, cf);
        },

        getForm: function(){
            if(this.form == undefined){
                this.form = new Ext.form.FormPanel({
                    border: false,
                    buttonAlign: 'right',
                    buttons: [
                        {
                            text: 'Salvar',
                            handler: function(){ this.commit(); },
                            scope: this
                        },
                        {
                            text: 'Cancelar',
                            handler: function() { this.destroy(); },
                            scope: this
                        }
                    ],
                    items: [ this.getFields() ]
                });
            }
            return this.form;
        },

        getData: function(){
            if(this.substituicao != undefined){
                var obj = toolkit.util.Ajax.request_json(
                        'POST',
                        toolkit.util.Normalize.controller_action(
                            'RHMovimentacaoSubstituicaoMembro','get_data'
                        ),
                        { substituicao: this.substituicao }
                );
                return obj;
            }else{ return undefined;}
        },

        commit: function() {
            var tipo = ((this.substituicao != undefined) ? ('/EDIT/' + this.substituicao) : '/NEW/0');
            var params = {'afastamento': this.afastamento};
            if(this.substituicao != undefined)
                params = {'afastamento': this.afastamento};
            var form = this.getForm().getForm();
            form.submit({
                scope: this,
                clientValidation: true,
                url: toolkit.util.Normalize.controller_action(
                    'RHMovimentacaoSubstituicaoMembro', 'commit' + tipo
                ),
                params: params,
                success: function(form, action){
                    if(action.result){
                        this.store_call_back.load();
                        this.destroy();
                    }else{
                        alert(action.result.messageException);
                    }
                },
                failure: function(form, action){
                    if(action.result){
                        this.store_call_back.load();
                        this.destroy();
                    }else{
                        alert(action.result.messageException);
                    }
                },
                waitMsg: 'salvando...'
            });
        },

        getStore: function(controller, params){
            return toolkit.util.Ajax.request_json(
                'POST', toolkit.util.Normalize.controller_action(controller, 'get_store'), params
            );
        },

        getFields: function(){
            return toolkit.rh.gestorafastamento.utils.FormSubstituicaoMembroFields({father: this});
        }
    }),

    CustomActionCrud: Ext.extend(Ext.Action,{
        constructor: function(cf) {
            cf.handler = function(){
                this.chamarExtCrud({controller: cf.controller});
            };
            toolkit.rh.gestorafastamento.utils.CustomActionCrud.superclass.constructor.call(this, cf);
        }
    }),

    ExtCrudCall: function(args) {

        this.store = (args.store ? args.store : undefined);

        this.controller = (args.controller ? args.controller : undefined);

        if(args.tipo == undefined || args.tipo == 'NEW')
            this.tipo = toolkit.widget.ExtCrudForm.TYPE.NEW;
        else if(args.tipo == 'EDIT')
            this.tipo = toolkit.widget.ExtCrudForm.TYPE.EDIT;
        else if(args.tipo == 'DELETE')
            this.tipo = 3;

        this.pk = (args.pk ? args.pk : undefined);

        this.fields = (args.fields ? args.fields : {});

        this.call = function(){
            new toolkit.widget.ExtCrudForm(
                {
                    store: this.store,
                    controller: this.controller,
                    reload_grid: function(){ this.store.reload(); }
                },
                this.tipo,
                (this.pk == undefined ? false : this.pk),
                this.fields
            ).show();
        };
    },

    MenuAfastamento: function(args) {
        return {
            text: 'Afastamentos',
            menu: [
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Recesso Forense - Membros',
                    controller: 'AFAAfastamentoRecessoForenseRestful',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Comparecer em juízo',
                    controller: 'AFAAfastamentoComparecimentoJuizo',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Candidatura',
                    controller: 'AFAAfastamentoCandidaturaRestful',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Competição desportiva ou representação cultural',
                    controller: 'AFAAfastamentoCompeticao',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Curso de formação de etapa de concurso público',
                    controller: 'AFAAfastamentoCursoConcurso',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Deslocamento até a nova sede',
                    controller: 'AFAAfastamentoDeslocamento',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Convocação da Justiça Eleitoral',
                    controller: 'AFAAfastamentoEleitoral',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Estudar no País/Exterior',
                    controller: 'AFAAfastamentoEstudar',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Exercício de Mandato Eletivo',
                    controller: 'AFAAfastamentoMandatoEletivo',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Missão Oficial no Exterior',
                    controller: 'AFAAfastamentoMissao',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Prisão',
                    controller: 'AFAAfastamentoPrisao',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Servir a outro Órgão',
                    controller: 'AFAAfastamentoOutroOrgao',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Servir no Tribunal do Juri',
                    controller: 'AFAAfastamentoServirJuri',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Suspensão',
                    controller: 'AFAAfastamentoSuspensao',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Treinamento (Palestras/Congressos/Seminários/Outros)',
                    controller: 'AFAAfastamentoTreinamento',
                    scope: args.scope
                })
            ]
        };
    },

    MenuLicenca: function(args) {
        return  {
            text: 'Licenças',
            menu: [
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Afastamento do Cônjuge/Companheiro',
                    controller: 'AFALicencaAfastamentoConjuge',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Atividade Política',
                    controller: 'AFALicencaAtividadePolitica',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Capacitação ou Especialização (3 meses por quinquênio)',
                    controller: 'AFALicencaCapacitacao',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Desempenho de Mandato Classista',
                    controller: 'AFALicencaMandatoClassista',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Doença em Pessoa da Família',
                    controller: 'AFALicencaDoencaPessoaFamilia',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Maternidade',
                    controller: 'AFALicencaMaternidade',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Serviço militar',
                    controller: 'AFALicencaServicoMilitar',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Tratamento de Saúde até 15 dias - Servidor',
                    controller: 'AFALicencaSaude3Dias',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Tratamento de Saúde até 30 dias - Membro',
                    controller: 'AFALicencaSaude30Dias',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Tratamento de Saúde Junta Médica',
                    controller: 'AFALicencaSaudeJuntaMedica',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Interesse Particular',
                    controller: 'AFALicencaInteresseParticular',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Tutoria ou Adoção',
                    controller: 'AFALicencaAdocao',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Folga Aniversário',
                    controller: 'AFAFolgaAniversario',
                    scope: args.scope
                })
            ]
        };
    },

    MenuAusencia: function(args) {
        return  {
            text: 'Ausências',
            menu: [
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Alistamento como eleitor',
                    controller: 'AFAAusenciaEleitor',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Casamento',
                    controller: 'AFAAusenciaCasamento',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Doação de sangue',
                    controller: 'AFAAusenciaDoacaoSangue',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Falecimento (Luto)',
                    controller: 'AFAAusenciaFalecimento',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Conclusão de TCC',
                    controller: 'AFAAusenciaConclusao',
                    scope: args.scope
                }),
                new toolkit.rh.gestorafastamento.utils.CustomActionCrud({
                    text: 'Paternidade/Tutoria ou Adoção',
                    controller: 'AFAAusenciaNascimento',
                    scope: args.scope
                })
            ]
        };
    },

    getDesignationField: function(designation, employee){
        this._designacaoField = Ext._create('core.fields.AutocompleteField', {
            fieldLabel: 'Órgão de Execução',
            allowBlank: false,
            rest: 'rh.employee.workplace.ownerlocation.Restful',
            name: 'designacao_substituido',
            preFilter: [{'property': 'servidor__matricula', 'level': 0, 'value': employee}],
            value: designation,
            readOnly: designation != undefined && designation != '' ? true : false,
        });
        return this._designacaoField;
    },

    FormSubstituicaoMembroFields: function(args) {
        var afastamento = (args.father.data_substituicao != undefined ? args.father.data_substituicao.afastamento : args.father.afastamento);
        args.father.afastamento = afastamento;
        var substituido_matricula = (args.father.data_substituicao ? args.father.data_substituicao.substituido_matricula : args.father.servidor);
        return new Ext.TabPanel({
            activeTab: 0,
            autoHeight: true,
            items: [
                {
                    'labelWidth': 115,
                    'autoHeight': true,
                    'layout': 'form',
                    'xtype': 'panel',
                    'defaults': {'width': 375},
                    'title': 'Dados',
                    'items': [
                        {
                          'displayField': 'description',
                          'fieldLabel': 'Afastamento',
                          'allowBlank': false,
                          'value': afastamento,
                          'readOnly': (afastamento ? true : false),
                          'hiddenName': 'afastamento',
                          'valueField': 'pk',
                          'conf': {'canAdd': false, 'canEdit': false},
                          'triggerAction': 'all',
                          'genericCrud': true,
                          'queryAction': 'query',
                          'model': {'name': 'baselicencaafastamento', 'app_label': 'afastamento'},
                          'hideTrigger': true,
                          'queryParam': 'keyword',
                          'xtype': 'autocompletefield'
                        },
                        this.getDesignationField(args.father.data_substituicao != undefined ? args.father.data_substituicao.designacao_substituido : '', substituido_matricula),
                        {
                            "disabled": args.father.data_substituicao != undefined ? true : false,
                            "value": args.father.data_substituicao != undefined ? args.father.data_substituicao.cargo_arquimedes : "",
                            "allowBlank": true,
                            "fieldLabel": "Cargo arquimedes",
                            "xtype": "modelchoicefield",
                            "triggerAction": "all",
                            "store": args.father.getStore("RHArqDesignacaoExercicio", {"origem": "form", "servidor": substituido_matricula, "cargo_arquimedes": (args.father.data_substituicao != undefined ? args.father.data_substituicao.cargo_arquimedes : undefined)}),
                            "hiddenName": "cargo_arquimedes",
                            "listeners": {
                                scope: this,
                                afterrender: function(cmp) {
                                    var recordSelected = cmp.getStore().getAt(0);
                                    if(recordSelected != undefined)
                                        cmp.setValue(recordSelected.get('field1'));
                                }
                            }
                        },
                        {
                            "displayField": "description",
                            "fieldLabel": "Posse substitu\u00eddo",
                            "allowBlank": false,
                            "father": "RHMovimentacaoSubstituicaoMembro",
                            "value": null,
                            "hiddenName": "posse",
                            "valueField": "pk",
                            "conf": {
                                // "addLabel": "Criar ...",
                                // "editLabel": "Visualizar registro ...",
                                "canAdd": false,
                                "canEdit": false
                            },
                            "triggerAction": "all",
                            "queryAction": "query",
                            "model": "MovimentacaoPosse",
                            "hideTrigger": true,
                            "queryParam": "keyword",
                            "crudController": "RHMovimentacaoPosse",
                            "xtype": "autocompletefield",
                            "value": args.father.data_substituicao != undefined ? args.father.data_substituicao.posse : null
                        },
                        {
                            'displayField': 'description',
                            'fieldLabel': 'Substituto',
                            'allowBlank': false,
                            'hiddenName': 'servidor',
                            'valueField': 'pk',
                            'conf': {'canAdd': false,'canEdit': false},
                            'triggerAction': 'all',
                            'queryAction': 'query_membro',
                            'model': 'Servidor',
                            'hideTrigger': true,
                            'queryParam': 'keyword',
                            'crudController': 'RHServidor',
                            'xtype': 'autocompletefield',
                            'defaultParams': {'matricula': substituido_matricula},
                            'value': args.father.data_substituicao != undefined ? args.father.data_substituicao.substituto : '',
                            'readOnly': args.father.data_substituicao != undefined ? true : false
                        },
                        {
                            'displayField': 'description',
                            'fieldLabel': 'Publica\u00e7\u00e3o in\u00edcio',
                            'allowBlank': false,
                            'value': args.father.data_substituicao != undefined ? args.father.data_substituicao.publicacao_movimentacao : '',
                            'hiddenName': 'publicacao_movimentacao',
                            'valueField': 'pk',
                            'conf': {
                                'addLabel': 'Criar ...',
                                'editLabel': 'Modificar ...',
                                'canAdd': true,
                                'canEdit': true
                            },
                            'triggerAction': 'all',
                            'queryAction': 'query',
                            'model': 'Publicacao',
                            'hideTrigger': true,
                            'queryParam': 'keyword',
                            'crudController': 'RHPublicacao',
                            'xtype': 'autocompletefield'
                        },
                        {
                            'displayField': 'description',
                            'fieldLabel': 'Documento Fim',
                            'allowBlank': true,
                            'value': args.father.data_substituicao != undefined ? args.father.data_substituicao.publicacao_fim : '',
                            'hiddenName': 'publicacao_fim',
                            'valueField': 'pk',
                            'conf': {
                                'addLabel': 'Criar ...',
                                'editLabel': 'Modificar ...',
                                'canAdd': true,
                                'canEdit': true
                            },
                            'triggerAction': 'all',
                            'queryAction': 'query',
                            'model': 'Publicacao',
                            'hideTrigger': true,
                            'queryParam': 'keyword',
                            'crudController': 'RHPublicacao',
                            'xtype': 'autocompletefield'
                        },
                        {
                            'allowBlank': false,
                            'fieldLabel': 'Data Início',
                            'xtype': 'datefield',
                            'format': 'd/m/Y',
                            'value': args.father.data_substituicao != undefined ? args.father.data_substituicao.data_inicio : '',
                            'name': 'data_inicio'
                        },
                        {
                            'allowBlank': true,
                            'fieldLabel': 'Data Prevista Fim',
                            'xtype': 'datefield',
                            'format': 'd/m/Y',
                            'value': args.father.data_substituicao != undefined ? args.father.data_substituicao.data_prevista : '',
                            'name': 'data_prevista'
                        },
                        {
                            'allowBlank': true,
                            'fieldLabel': 'Data Fim',
                            'xtype': 'datefield',
                            'format': 'd/m/Y',
                            'value': args.father.data_substituicao != undefined ? args.father.data_substituicao.data_fim : '',
                            'name': 'data_fim'
                        },
                        {
                            'displayField': 'description',
                            'fieldLabel': 'Documento Revogação/Alteração',
                            'allowBlank': true,
                            'value': args.father.data_substituicao != undefined ? args.father.data_substituicao.publicacao_alteracao : '',
                            'hiddenName': 'publicacao_alteracao',
                            'valueField': 'pk',
                            'conf': {
                                'addLabel': 'Criar ...',
                                'editLabel': 'Modificar ...',
                                'canAdd': true,
                                'canEdit': true
                            },
                            'triggerAction': 'all',
                            'queryAction': 'query',
                            'model': 'Publicacao',
                            'hideTrigger': true,
                            'queryParam': 'keyword',
                            'crudController': 'RHPublicacao',
                            'xtype': 'autocompletefield'
                        },
                        {
                            'checked': true,
                            'fieldLabel': 'Gera Anota\u00e7\u00e3o',
                            'xtype': 'checkbox',
                            'name': 'anota',
                            'allowBlank': true
                        }
                    ],
                    'style': 'padding:0.5em'
                },
                {
                    'labelWidth': 115,
                    'autoHeight': true,
                    'layout': 'form',
                    'xtype': 'panel',
                    'defaults': {'width': 375},
                    'title': 'Outros',
                    'items': [
                        {
                            'allowBlank': true,
                            'fieldLabel': 'Texto',
                            'xtype': 'xhtmleditor',
                            'value': '',
                            'name': 'texto'
                        }
                    ],
                    'style': 'padding:0.5em'
                }
            ]
        });
    },

    FormInativacaoMembroFields: function(args) {
        return new Ext.TabPanel({
            activeTab: 0,
            autoHeight: true,
            items: [
                {
                    'labelWidth': 115,
                    'autoHeight': true,
                    'layout': 'form',
                    'xtype': 'panel',
                    'defaults': {'width': 375},
                    'title': 'Dados',
                    'items': [
                        {
                            'displayField': 'description',
                            'fieldLabel': 'Cargo',
                            'allowBlank': false,
                            'readOnly': args.father.data_inativacao != undefined ? true : false,
                            'value': args.father.data_inativacao != undefined ? args.father.data_inativacao.posse : '',
                            'hiddenName': 'posse',
                            'valueField': 'pk',
                            'conf': {
                                'addLabel': 'Criar ...',
                                'editLabel': 'Modificar ...',
                                'canAdd': false,
                                'canEdit': false
                            },
                            'triggerAction': 'all',
                            'queryAction': 'query',
                            'model': 'MovimentacaoPosse',
                            'hideTrigger': true,
                            'queryParam': 'keyword',
                            'crudController': 'RHMovimentacaoPosse',
                            'xtype': 'autocompletefield'
                        },
                        {
                            'displayField': 'description',
                            'fieldLabel': 'Publicação Inativação',
                            'allowBlank': false,
                            'value': args.father.data_inativacao != undefined ? args.father.data_inativacao.publicacao_inativacao : '',
                            'hiddenName': 'publicacao_inativacao',
                            'valueField': 'pk',
                            'conf': {
                                'addLabel': 'Criar ...',
                                'editLabel': 'Modificar ...',
                                'canAdd': true,
                                'canEdit': true
                            },
                            'triggerAction': 'all',
                            'queryAction': 'query',
                            'model': 'Publicacao',
                            'hideTrigger': true,
                            'queryParam': 'keyword',
                            'crudController': 'RHPublicacao',
                            'xtype': 'autocompletefield'
                        },
                        {
                            'displayField': 'description',
                            'fieldLabel': 'Publicação Ativação',
                            'allowBlank': true,
                            'value': args.father.data_inativacao != undefined ? args.father.data_inativacao.publicacao_ativacao : '',
                            'hiddenName': 'publicacao_ativacao',
                            'valueField': 'pk',
                            'conf': {
                                'addLabel': 'Criar ...',
                                'editLabel': 'Modificar ...',
                                'canAdd': true,
                                'canEdit': true
                            },
                            'triggerAction': 'all',
                            'queryAction': 'query',
                            'model': 'Publicacao',
                            'hideTrigger': true,
                            'queryParam': 'keyword',
                            'crudController': 'RHPublicacao',
                            'xtype': 'autocompletefield'
                        },
                        {
                            'allowBlank': true,
                            'fieldLabel': 'Data Início',
                            'xtype': 'datefield',
                            'format': 'd/m/Y',
                            'value': args.father.data_inativacao != undefined ? args.father.data_inativacao.data_inicio : '',
                            'name': 'data_inicio'
                        },
                        {
                            'allowBlank': true,
                            'fieldLabel': 'Data Prevista Fim',
                            'xtype': 'datefield',
                            'format': 'd/m/Y',
                            'value': args.father.data_inativacao != undefined ? args.father.data_inativacao.data_prevista : '',
                            'name': 'data_prevista'
                        },
                        {
                            'allowBlank': true,
                            'fieldLabel': 'Data Fim',
                            'xtype': 'datefield',
                            'format': 'd/m/Y',
                            'value': args.father.data_inativacao != undefined ? args.father.data_inativacao.data_fim : '',
                            'name': 'data_fim'
                        },
                        {
                            'displayField': 'description',
                            'fieldLabel': 'Documento Revogação/Alteração',
                            'allowBlank': true,
                            'value': args.father.data_inativacao != undefined ? args.father.data_inativacao.publicacao_alteracao : '',
                            'hiddenName': 'publicacao_alteracao',
                            'valueField': 'pk',
                            'conf': {
                                'addLabel': 'Criar ...',
                                'editLabel': 'Modificar ...',
                                'canAdd': true,
                                'canEdit': true
                            },
                            'triggerAction': 'all',
                            'queryAction': 'query',
                            'model': 'Publicacao',
                            'hideTrigger': true,
                            'queryParam': 'keyword',
                            'crudController': 'RHPublicacao',
                            'xtype': 'autocompletefield'
                        }
                    ],
                    'style': 'padding:0.5em'
                }
            ]
        });
    },

    MenuSubstituicao: function(args) {
        return new Ext.menu.Menu({
            id: 'mainMenu',
            split: true,
            defaultStyle: 'splitbutton',
            style: { overflow: 'visible'},
            scope: this,
            items: [
                toolkit.rh.gestorafastamento.utils.MenuSubstituicaoMembro(args.membro),
                toolkit.rh.gestorafastamento.utils.MenuSubstituicaoServidor(args.servidor)
            ]
        });
    },

    MenuSubstituicaoMembro: function(args) {
        return new Ext.Action({
            scope: args.scope,
            text: 'Membro - Substituições e Inativações',
            handler: args.handler,
            iconCls: 'icon-progressoes icon-progressoes-update',
            itemId: 'membroSubstituicaoInativacao'
        });
    },

    MenuSubstituicaoServidor: function(args) {
        return new Ext.Action({
            scope: args.scope,
            text: 'Servidor - Substituição',
            handler: args.handler,
            iconCls: 'icon-progressoes icon-progressoes-update',
            itemId: 'servidorSubstituicao'
        });
    },

    MenuSubstituicaoGeral: function(args) {
        return new Ext.menu.Menu({
            id: 'mainMenu',
            split: true,
            defaultStyle: 'splitbutton',
            style: { overflow: 'visible' },
            scope: this,
            items: [
                toolkit.rh.gestorafastamento.utils.MenuSubstituicaoFormMembro(args.membro),
                toolkit.rh.gestorafastamento.utils.MenuSubstituicaoFormServidor(args.servidor)
            ]
        });
    },

    MenuSubstituicaoFormMembro: function(args) {
        return new Ext.Action({
            scope: args.scope,
            text: 'Membro - Substituição',
            handler: args.handler,
            iconCls: 'icon-progressoes icon-progressoes-update',
            itemId: 'membroSubstituicaoInativacao'
        });
    },

    MenuSubstituicaoFormServidor: function(args) {
        return new Ext.Action({
            scope: args.scope,
            text: 'Servidor - Substituição',
            handler: args.handler,
            iconCls: 'icon-progressoes icon-progressoes-update',
            itemId: 'servidorSubstituicao'
        });
    }
});
