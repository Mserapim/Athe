/**
 *
 **/
Ext._define('common.siatu.solicitacao.WindowGerente', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.solicitacao.Restful',

    width: 750,

    autoHeight: true,

    tbar: [
        {
            text: 'Importar eDoc',
            handler: function(btn) {

                var callback = function(selected)
                {
                    var user_id = selected.get('user');
                    if(user_id)
                    {
                        var form = this.getFormPanel().getForm();
                        this.getResquesterPhone(selected.get('user'), function(opts, success, request) {
                            var rst = Ext.decode(request.responseText),
                                values = {
                                    servico: 4,
                                    solicitante: user_id,
                                    telefone: rst.values.telefone,
                                    tipo: 3,
                                    descricao_problema: selected.get('content_stripedtags'),
                                };

                            form.setValues(values);
                        });
                    }
                    else
                    {
                        var code = selected.get('code'),
                            person = selected.get('interested_unicode');

                        Ext.Msg.alert('Erro', person +', interessado no protocolo '+ code +' não possui usuário associado.');
                    }
                }

                Ext._create('edocs.protocolo.SelectProtocolWindow', {
                    onOk: {
                        scope: btn.ownerCt.ownerCt,
                        fn: callback
                    }
                }).show();
            }
        }
    ],

    getResquesterPhone: function(requester_id, callback) {
        var rest = this.factoryRestful(),
            route = rest.getRoute('telefone_usuario', requester_id, 'GET', {
                scope: this,
                callback: callback
            });

        rest.doRequest(route);
    },

    getTipoField: function(){
        if(!this._tipo){
            this._tipo = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Tipo',
                hiddenName: 'tipo',
                width: 220,
                triggerAction: 'all',
                allowBlank: false,
                store: [
                    [1, 'Email'],
                    [2, 'Telefone'],
                    [3, 'Documento'],
                    [4, 'Verbal'],
                ],
            });
        }

        return this._tipo;
    },

    getSolicitanteField: function(){
        if(!this._solicitanteField){
            this._solicitanteField = Ext._create('core.fields.AutocompleteField', {
                rest: 'auth.UserRestful',
                name: 'solicitante',
                fieldLabel: 'Solicitante',
                displayField: 'pessoa_nome',
                triggerAction: 'all',
                width: 615,
                comboListeners: {
                    scope: this,
                    changevalid:function(combo, id, start, valid) {
                        if(valid == true){
                            if(combo.getValue() != this.OldValueSolicitante){
                                this.OldValueSolicitante = combo.getValue()
                                this.atualiza(id)
                                this.getChamadoField().reset()
                                this.getChamadoField().setPreFilter([
                                    {property:'chamado_reincidente__isnull',value:true, stage: 0},
                                    {property:'solicitacao__solicitante',value: id, stage: 1},
                                    {property:'status_atual__status',value: this.getParams().concluido, stage: 2},
                                ])
                                this.getChamadoField().getComboField().getStore().load({})
                            }
                        }
                    },
                },
                gridConfig: {
                    columnAction: false,
                    allowCreate: false,
                    allowUpdate: false,
                    allowRemove: false,
                    listeners: {
                        scope: this,
                        render: function(grid){
                            tbar = grid.getToolbar()
                            tbar.remove(tbar.getComponent(0))//Novo
                            tbar.remove(tbar.getComponent(0))//Editar
                            tbar.remove(tbar.getComponent(0))//Remover
                        },
                    }
                }
            });
        }

        return this._solicitanteField
    },

    getServicoField: function(){
        if(!this._servico){
            this._servico = Ext._create('core.fields.FoldedRestfulField', {
                restTree: 'common.siatu.servico.Tree',
                fieldLabel: 'Servico',
                name: 'servico',
                width: 615,
                treeConfig:{
                    listeners: {
                        render: function(tree){
                            tbar = tree.getToolbar()
                            tbar.remove(tbar.getComponent(0))//Adicionar
                            tbar.remove(tbar.getComponent(0))//Editar
                            tbar.remove(tbar.getComponent(0))//Remover
                            tbar.remove(tbar.getComponent(0))//Separador
                            tbar.remove(tbar.getComponent(0))//Mover
                            tbar.remove(tbar.getComponent(0))//Separador
                        },
                        load: function(node) {
                            Ext.each(
                                node.childNodes,
                                function(childNode) {
                                    if((childNode.text == 'Administrativo') ||
                                       (childNode.text == 'Almoxarifado') ||
                                       (childNode.text == 'Informática') ||
                                       (childNode.text == 'Banco de dados') ||
                                       (childNode.text == 'Manutenção de Informática') ||
                                       (childNode.text == 'Redes e comunicação') ||
                                       (childNode.text == 'Sistemas de informação') ||
                                       (childNode.text == 'Transporte')) {
                                            childNode.disable();
                                    }
                                },
                                this
                            );
                        }
                    }
                }
            })
        }

        return this._servico;
    },

    getReincidenciaField: function(){
        if(!this._reincidencia){
            this._reincidencia = Ext._create('Ext.form.Checkbox', {
                name: 'reincidencia',
                fieldLabel: 'Este problema já aconteceu outra vez?',
                allowBlank: true,
            })
            this._reincidencia.on({
                scope: this,
                check: function(checkbox, checked) {
                    if (checked){
                        this.getChamadoField().enable()
                        this.getChamadoField().show();
                    }
                    else{
                        this.getChamadoField().hide();
                        this.getChamadoField().disable()
                        this.getChamadoField().reset()
                    }
                }
            });

        }

        return this._reincidencia
    },

    getChamadoField: function(){
        if (!this._chamado){
            this._chamado = Ext._create('core.fields.AutocompleteField', {
                rest: 'common.siatu.chamado.Restful',
                name: 'chamado_anterior',
                fieldLabel: 'Chamado',
                displayField: 'identificacao',
                gridColumnAction: false,
                gridListeners:{
                    render: function(grid){
                        tbar = grid.getToolbar()
                        tbar.remove(tbar.getComponent(0))//Editar
                        tbar.remove(tbar.getComponent(0))//Remover
                    }
                },
                disabled: true,
                hidden: true
            });
        }

        return this._chamado
    },

    getPanelInfoSolicitante: function() {
        if(!this._infoSolicitante)
            this._infoSolicitante = Ext._create('Ext.form.FieldSet',{
                    xtype: 'fieldset',
                    title: 'Solicitante',
                    autoHeight:true,
                    hidden: true,
                    items: [
                        {
                            xtype: 'displayfield',
                            name: 'nome',
                            fieldLabel: 'Nome',
                        },
                        {
                            xtype: 'displayfield',
                            name: 'lotacao',
                            fieldLabel: 'Lotação',
                        },
                        {
                            xtype: 'displayfield',
                            name: 'membro',
                            fieldLabel: 'Membro',
                        },
                        {
                            xtype: 'displayfield',
                            name: 'cidade',
                            fieldLabel: 'Cidade',
                        }
                    ]

                })
        return this._infoSolicitante
    },

    atualiza: function(solicitante) {
        this.store = Ext._create('Ext.data.Store', {
            proxy: Ext._create('Ext.data.HttpProxy', {
                api: {
                    read: core.callAction("AUTHUserRestful", "action_info_user_servidor", solicitante)
                },
                disableCaching: false,
                defaultHeaders: this.rest.defaultHeaders,
            }),
            reader: Ext._create('Ext.data.JsonReader', {
                idProperty: 'nome',
                root: 'result',
                totalProperty: 'count',
                successProperty: 'success',
                messageProperty: 'message',
                fields: [
                        {name: 'nome', type: 'string'},
                        {name: 'lotacao', type: 'string'},
                        {name: 'membro', type: 'string'},
                        {name: 'cidade', type: 'string'},
                        {name: 'ramal', type: 'string'},
                        ]
            }),
            autoLoad: false
        })

        this.store.load({callback: this.preenche, scope: this})


        var restSolicitante = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Buscando informações do usuário...'});
        mask.show();
        restSolicitante.doRequest(
            restSolicitante.getRoute('telefone_usuario', solicitante, 'GET', {
                scope: this,
                callback: function(opts, success, request) {
                    mask.hide();
                    mask = null;
                    if(success) {
                        var rst = Ext.decode(request.responseText);
                        if(rst.success) {
                            this.getFormPanel().getForm().setValues(rst.values);
                        }else{
                            this.getFormPanel().getForm().setValues({telefone: ""});
                        }
                    }else{
                        this.getFormPanel().getForm().setValues({telefone: ""});
                    }
                }
            })
        );
    },

    preenche: function(record, option, success) {

        if(success){
            this.getFormPanel().getForm().loadRecord(record[0])
            this.getPanelInfoSolicitante().show()
        }
        else{
            this.getPanelInfoSolicitante().hide()
            Ext.Msg.show({
                title: 'Informações do Solicitante',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: this.store.reader.jsonData.message
            });
        }
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getServicoField(),
                    this.getSolicitanteField(),
                    this.getPanelInfoSolicitante(),
                    {
                        xtype: 'fonefield',
                        width: 220,
                        name: 'telefone',
                        fieldLabel: 'Telefone',
                        allowBlank: true,
                    },
                    this.getTipoField(),
                    {
                        xtype: 'textarea',
                        width: 615,
                        name: 'descricao_problema',
                        fieldLabel: 'Problema',
                        allowBlank: true,
                    },
                    this.getReincidenciaField(),
                    this.getChamadoField(),
                    {
                        title: 'Deseja anexar uma foto da tela ou um arquivo pra ajudar na explicação do problema?: ',
                        flex: 1,
                        border: false,
                        items: [
                            this.getArquivoGrid(),
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

    getArquivoGrid: function(){
        if(!this._arquivogrid) {
            this._arquivogrid = Ext._create('common.siatu.chamado.anexo.Grid', {
                height:200,
                disabled: true,
                gridAutoLoad: false,
            });
        }
        // console.log(this._arquivogrid.getStore());
        this._arquivogrid.getStore().removeAll();

        return this._arquivogrid
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    // console.log(instance);
                    this.getArquivoGrid().setParam('chamado', instance.chamado);
                    this.getArquivoGrid().setFilterProperty('chamado__id', instance.chamado, 1001);
                    this.getArquivoGrid().enable();
                    this.oId = instance.pk;
                    this.action = 'update';
                    // this.observer(cfg);
                }
            }
        });

        common.siatu.solicitacao.WindowGerente.superclass.constructor.call(this, cfg);

        this.getChamadoField().setPreFilter([
            {property:'solicitacao__solicitante',value: null, stage: 1},
        ]);
    }
});
