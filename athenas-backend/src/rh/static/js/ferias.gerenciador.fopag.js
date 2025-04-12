Ext.ns('toolkit.rh.ferias');


Ext.apply(
    toolkit.rh.ferias,
    {
//---------------------------------------------------------------------------
        GestorPASFolhaTerco: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function() {
                    if(!this.formPanel) {
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            border: false,
                            defaults: {
                                width: '420'
                            },
                            items: [
                                {
                                    hiddenName: 'folha_terco',
                                    name: 'cb_folha_terco',
                                    fieldLabel: '1/3 Constitucional',
                                    xtype: 'combo',
                                    displayField: 'description',
                                    valueField: 'pk',
                                    editable: false,
                                    mode: 'local',
                                    width: 360,
                                    triggerAction: 'all',
                                    emptyText: "Selecione uma folha",
                                    store: new Ext.data.JsonStore({
                                        url: toolkit.util.Normalize.controller_action(
                                            'FRSGestorFerias',
                                            'list_folha_terco'
                                        ),
                                        autoLoad: true,
                                        baseParams: {'pas': this.configuration.pas.pk},
                                        root: 'result',
                                        fields: ['pk', 'description']
                                    }),
                                    conf: {
                                        canEdit: false,
                                        canAdd: false
                                    }

                                }
                            ]
                        });
                    }

                    return this.formPanel
                },

                constructor: function(father, pas, callback) {
                    var cf = {
                        title: 'Atualização do Terço Constitucional',
                        closable: true,
                        resizable: false,
                        modal: true,
                        border: false,
                        width: 500,
                        configuration: {
                            pas: pas,
                            callback: callback || function(){}
                        },
                        buttons: [
                            {
                                text: 'Salvar',
                                scope: this,
                                handler: this.commit
                            },
                            {
                                text: 'Cancelar',
                                scope: this,
                                handler: this.destroy
                            }
                        ]
                    };

                    toolkit.rh.ferias.GestorPASFolhaTerco.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());
                },

                commit: function() {
                    var form = this.getFormPanel().getForm();

                    form.waitMsgTarget = this.getEl();
                    form.submit({
                        waitMsg: 'Gravando dados do terço constitucional',
                        url: toolkit.util.Normalize.controller_action(
                            'FRSGestorFerias',
                            'update_folha_terco'
                        ),
                        params: {
                            pas: this.configuration.pas.pk
                        },
                        success: function(form, request) {
                            this.configuration.callback(request.result.result);
                            this.destroy();
                        },
                        failure: function() {
                            alert('Não foi possivel atualizar terço constitucional.');
                        },
                        scope: this
                    })
                }
            }
        )


        //----------------------------------------------------------------------------
    }

);

Ext.apply(
    toolkit.rh.ferias,
    {
        GestorFeriasFolhaPagamento:Ext.extend(
            toolkit.rh.ferias.GestorFerias,
            {
                _gerenciarPasu: function(){
                    if(this.getSelectionsPAS().getCount()==1){
                        pas = this.getSelectedPAS();
                        var scope= this;
                        new toolkit.rh.ferias.GestorPASFolhaTerco(
                            this,
                            pas.data,
                            function(params){scope.refresh();}
                        ).show();

                    }else{
                        var msg = 'Erro na seleção';
                        if(this.getSelectionsPAS().getCount()>1)
                            msg= 'Você deve selecionar apenas o período de um servidor para gerenciar suas parcelas.!';
                        else
                            msg= 'Você deve selecionar um período e um servidor para gerenciar suas parcelas.!';
                        Ext.MessageBox.show({
                           title: 'Informação',
                           msg: msg,
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.INFO
                        });
                    }
                },
                getPASGridToolbar: function() {
                    if(!this.gridToolbar) {

                        var buttons= [
                            {
                                text: 'Gerenciamento - 1/3 de Férias',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/rh/images/folha-de-pagamento.png',
                                split: true,
                                defaultStyle: 'splitbutton',
                                menu: [
                                    this.act_gerenciarPasu,
                                    this.act_indenizarPas,
                                    this.act_desbloquear,
                                ]
                            },
                            '-'
                        ]

                    }
                    this.gridToolbar= this.pasGridPanel.getTopToolbar();
                    this.gridToolbar.insertButton(0,buttons);
                    return this.gridToolbar;

                }
            }
        )
    }
);
