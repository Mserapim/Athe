/**
 *
 **/
Ext._define('common.siatu.configuration.distribuicao.Panel', {
    extend: 'core.RestfulPanel',


    rest: 'common.siatu.configuration.distribuicao.Restful',

    setParam: function(key, value) {
        this.params = core.nullValue(this.params, {});
        this.params[key] = value;
    },

    _prepareSuccessCallback: function(callback) {
        var wnd = this;
        var success = callback.success;

        function foo(args) {
            core.invokeCallback(
                success,
                args
            );
        };

        callback.success = {
            fn: foo
        };

        return callback
    },

    preenche: function(servico){
        var restServico = Ext._create('common.siatu.servico.Restful',{})
        var rest = this.factoryRestful();
        restServico.get(
            servico,
            {
                success: {
                    scope: this,
                    fn: function(instance) {
                        rest.get(
                            instance.dist_automatica,
                            {
                                success: {
                                    scope: this,
                                    fn: function(instance) {
                                        this.getPanelSolicitantes().setDisabled(false)
                                        this.oId = instance.pk
                                        this.getFormPanel().getForm().setValues(
                                            instance
                                        );
                                        this.getListUserGrid().setFilterProperty('pk__in', instance.solicitantes)
                                    }
                                }
                            },
                            {
                                el: this.getEl()
                            }
                        )
                    }
                },
            },
            {
                el: this.getEl()
            }
        )
    },

    getUserGrid: function(){
        if(!this._userGrid){
            this._userGrid = Ext._create('auth.UserGrid', {
                title:'Usuários',
                flex:0.5,
                columnAction:false,
            });

            this._userGrid.setSortProperty('servidor__pessoa_fisica__nome', 'ASC', false)
            this._userGrid.setSortProperty('username', 'ASC', false)

            var tbar = this._userGrid.getToolbar()
            tbar.remove(tbar.getComponent(0)); // Adicionar
            tbar.remove(tbar.getComponent(0)); // Remover
            tbar.remove(tbar.getComponent(0)); //Separador
        }

         return this._userGrid;
    },

    getListUserGrid: function(){
        if(!this._listUserGrid){
            this._listUserGrid = Ext._create('auth.UserGrid', {
                title:'Solicitantes a retirar da distribuição automática',
                flex:0.5,
                columnAction:false,
                border: true,
                gridAutoLoad: false,
            });

            this._listUserGrid.setSortProperty('servidor__pessoa_fisica__nome', 'ASC', false)
            this._listUserGrid.setSortProperty('username', 'ASC', false)

            var tbar = this._listUserGrid.getToolbar()
            tbar.remove(tbar.getComponent(0)); // Adicionar
            tbar.remove(tbar.getComponent(0)); // Remover
            tbar.remove(tbar.getComponent(0)); //Separador
        }

         return this._listUserGrid;
    },

    getPanelSolicitantes: function() {
        if(!this._panelSolicitante)
            this._panelSolicitante = Ext._create('Ext.Panel',{
                layout: 'hbox',
                flex: 1.0,
                split:true,
                disabled: true,
                bodyStyle: {
                    'border-left': 0,
                    'border-right': 0,
                },
                layoutConfig: {
                    align: 'stretch',
                },
                items:[
                    this.getUserGrid(),
                    this.getControlPanel(),
                    this.getListUserGrid(),
                ]

            });

        return this._panelSolicitante
    },

    getServicoField: function(){
        if(!this._servico){
            this._servico = Ext._create('core.fields.FoldedRestfulField', {
                restTree: 'common.siatu.servico.Tree',
                fieldLabel: 'Selecione um serviço',
                name: 'servico',
                width: 265,
                treeConfig:{
                    listeners: {
                        scope: this,
                        render: function(tree){
                            // Filtrar apenas os servicos do gerente
                            // tree.getLoader().baseParams = {filter: Ext.encode([{"property":"pk__in","value":this.lista_servicos,"stage":0}])}
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
                                    if(this.lista_servicos.indexOf(parseInt(childNode.id)) == -1){
                                        childNode.disable();
                                    }
                                },
                                this
                            );
                        },
                    }
                }
            })

            this._servico.getValueField().setReadOnly(true);

            this._servico.getValueField().on({
                scope: this,
                change: function(fold, newValue, old) {
                    newValue = parseInt(newValue)

                    this.preenche(newValue)
                }
            });
        }

        return this._servico;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth:120,
                layout: 'vbox',
                layoutConfig:{
                    align: 'stretch',
                },
                items: [
                    {
                    layout: 'form',
                    height: 180,
                    items:[
                        this.getServicoField(),
                        {
                            xtype:'fieldset',
                            title: 'Tipo atendimento',
                            autoHeight:true,
                            items:[
                            {
                                xtype: 'checkbox',
                                name: 'sistema',
                                boxLabel: 'Sistema',
                                allowBlank: true,
                                hideLabel: true,
                            },
                            {
                                xtype: 'checkbox',
                                name: 'email',
                                boxLabel: 'Email',
                                allowBlank: true,
                                hideLabel: true,
                            },
                            {
                                xtype: 'checkbox',
                                name: 'telefone',
                                boxLabel: 'Telefone',
                                allowBlank: true,
                                hideLabel: true,
                            },
                            {
                                xtype: 'checkbox',
                                name: 'documento',
                                boxLabel: 'Documento',
                                allowBlank: true,
                                hideLabel: true,
                            },
                            {
                                xtype: 'checkbox',
                                name: 'verbal',
                                boxLabel: 'Verbal',
                                allowBlank: true,
                                hideLabel: true,
                            }
                            ]
                        },
                    ]

                    },
                    this.getPanelSolicitantes(),
                ]
            });

        return this._formPanel;
    },

    getControlPanel: function() {
        if(!this._controlPanelAtendente)
            this._controlPanelAtendente = Ext._create('Ext.Panel', {
                width: 40,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0
                },
                items: [
                    {
                        xtype: 'panel',
                        flex: 1.0
                    },
                    {
                        xtype: 'button',
                        text: '',
                        iconCls: 'icon-siatu icon-siatu-move-right',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() {  this.addSelected() }
                    },
                    {
                        xtype: 'panel',
                        height:10,
                    },
                    {
                        xtype: 'button',
                        text: '',
                        iconCls: 'icon-siatu icon-siatu-move-left',
                        width: 28,
                        height: 30,
                        style: {
                            padding: '2px 0 0 0'
                        },
                        scope: this,
                        handler: function() { this.removeSelected()}
                    },
                    {
                        xtype: 'panel',
                        flex: 1.0
                    }
                ]
            });

        return this._controlPanelAtendente;
    },

    addSelected: function() {
        var items = new Array();
        var store1 = this.getListUserGrid().getStore();
        var selections = this.getUserGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há usuário selecionado para adicionar à lista')
            return '';
        }

        selections.map(
            function(record) {
                store1.add(record)
            }
        );

        var rec=store1.getRange()

        for (i=0; i<rec.length; i++){
            items.push(rec[i].get('pk'))
        }

        this.setParam('solicitantes',items)
    },

    removeSelected: function() {
        var items = new Array();
        var store1 = this.getListUserGrid().getStore();
        var selections = this.getListUserGrid().getSelectionModel().getSelections();

        if(selections.length==0){
            console.debug('Não há usuário selecionado para remover da lista')
            return '';
        }

        selections.map(
            function(record) {
                store1.remove(record)
            }
        );

        var rec=store1.getRange()

        for (i=0; i<rec.length; i++){
            items.push(rec[i].get('pk'))
        }


        this.setParam('solicitantes',items)
    },

    verifica: function(){
        if(this.oId)
            this.save()
        else
            Ext.Msg.show({
                title: 'Erro',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Favor selecionar um serviço.'
            });
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    xtype: 'button',
                    text: 'Salvar',
                    width: 100,
                    height: 25,
                    scope: this,
                    handler: this.verifica,
                }
            ]
        }

        return this._buttons
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.lista_servicos = cfg.lista_servicos

        Ext.applyIf(
            cfg,
            {
                layout: 'fit',
                labelWidth:150,
                labelAlign:'right',
                action: 'update',
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            Ext.Msg.show({
                                title: 'Salvar',
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK,
                                msg: 'Operação realizada com sucesso.'
                            });
                        }
                    }
                }
            }
        );

        common.siatu.configuration.distribuicao.Panel.superclass.constructor.call(this, cfg);
    }
})
