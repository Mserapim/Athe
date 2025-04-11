/**
 *
 **/
Ext._define('edocs.processo.admin.processoAdminWindow', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.processo.admin.processoAdminRestful',

    actionTitles: {
        create: 'Novo Processo',
        update: 'Editando Processo',
        remove: 'Remover',
        read: 'Carregar'
    },

    width: 705,

    getReferenciasGrid: function() {
        if (!this._referenciasGrid) {
            this._referenciasGrid = Ext._create('edocs.processo.referencia.Grid', {
                title: 'Referências',
                disabled: true,
                gridAutoLoad: false
            });
        }

        return this._referenciasGrid;
    },

    getProcessMatterGrid: function() {
        if (!this._processMatter) {
            this._processMatter = Ext._create('edocs.processo.taxonomy.MatterGrid',{
                title: 'Assunto',
                height: 400,
                border: false,
                disabled: true,
                gridAutoLoad: true,
                hideItemsToolbar: ['search', 'download'],
                columnAction: false,
            });
            this._processMatter.getToolbar().add([
                '->',
                '-',
                {
                    text: 'Definir assunto principal',
                    iconCls: 'icon-edocs icon-protocolo-close-protocol',
                    scope: this,
                    handler: this.definePrincipal
                },
                '-'
            ]);
        }

        return this._processMatter;
    },

    definePrincipal: function() {

        var rest = this.getProcessMatterGrid().factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'definindo assunto principal...'});
        var selected = this.getProcessMatterGrid().getSelectionModel().getSelected();
        var values = {};

        values.process = this.oId;

        if(selected) {
            mask.show();
            rest.definePrincipal(
                selected.get('pk'),
                values,
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) {
                            core.invokeCallback((this.callback || {}).success);
                            this.getProcessMatterGrid().getStore().reload();
                        }
                        else
                            Ext.Msg.show({
                                title: 'Definir assunto principal',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                    }
                },
                {
                    scope: this,
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Definir assunto principal',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    scope: this,
                    fn: function() {
                        mask.hide();
                    }
                }
            );
        } else {
            Ext.Msg.show({
                title: 'Definir assunto principal',
                msg: 'Primeiro selecione um assunto.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getAttachmentGrid: function() {
      if (!this._attachmentGrid)
          this._attachmentGrid = Ext._create('edocs.protocolo.AttachmentGrid', {
              region: 'center',
              title: 'Anexos',
              disabled: true,
              gridAutoLoad: false
          });

        return this._attachmentGrid;
    },

    getInterestedM2MField: function() {
        if (!this._getInterestedM2MField)
            this._getInterestedM2MField = Ext._create('core.fields.RelatedRestfulField', {
                xtype: 'rest-relatedfield',
                hideLabel: true,
                allowBlank: true,
                border: false,
                name: 'interessados',
                displayField: 'nome',
                relatedname: 'interessados',
                width: 681,
                height: 423,
                rest: 'edocs.processo.consulta.processoComumRestful',
                sourceRest: 'rh.person.Restful',
                emptyText: 'Nome, CPF ou CNPJ (somente números)'
            });

        return this._getInterestedM2MField;
    },

    getInterestedPanel: function(cfg) {
        if (!this._interestedPanel)
            this._interestedPanel = Ext._create('Ext.Panel', {
                title: 'Interessados',
                frame: true,
                items: this.getInterestedM2MField()
            });

        return this._interestedPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        height: 445,
                        defaults: {
                            boxMinHeight: 320,
                            boxMaxHeight: 555
                        },
                        border: false,
                        items: [
                            {
                                xtype: "panel",
                                layout: "form",
                                frame: true,
                                title: "Informações",
                                border: false,
                                labelWidth: 70,
                                scope: this,
                                items: this.getGeral()
                            },
                            this.getProcessMatterGrid(),
                            this.getInterestedPanel(),
                            this.getAttachmentGrid(),
                            this.getReferenciasGrid()
                        ]
                    })
                ]
            });

        return this._formPanel;
    },

    getGeral: function() {
            var items = [];
            var width = 600;
            if (this.action == 'update') {
                items.push({
                    width: width,
                    name: "codigo_processo",
                    fieldLabel: "Processo",
                    xtype: "textfield",
                    readOnly: true,
                });
            }
            if (this.action == 'create') {
                items.push([
                {
                    width: width,
                    hiddenName: "unidade_gestora",
                    fieldLabel: "Un. Gestora",
                    xtype: "combo",
                    autoSelect: true,
                    value: 'PGJ-0701',
                    hiddenValue: '0701',
                    triggerAction: 'all',
                    store: [
                        ['0701', 'PGJ-0701'],
                        ['0805', 'FUNCESAF-0805'],
                    ]
                },
                {
                    xtype: "choicefield",
                    width: width,
                    fieldLabel: "Ano",
                    hiddenName: "ano",
                    choiceId: "epadm.ANO_EPADM"
                },
                {
                    width: width,
                    name: "numero",
                    fieldLabel: "Numero",
                    xtype: "numberfield",
                }]);
            }
            items.push({
                width: width,
                allowBlank: false,
                validateOnBlur: true,
                hiddenName: "orgao_geral_origem",
                fieldLabel: "Origem",
                xtype: "combo",
                displayField: "description",
                valueField: "id",
                store: toolkit.util.Ajax.request_json(
                    "POST",
                    toolkit.util.Normalize.controller_action(
                        "EDOCBox",
                        "get_store",
                        ["orgao_geral_origem"]
                    )
                ),
                triggerAction: "all",
                mode: 'local',
            });
            items.push({
                width: width,
                allowBlank: false,
                xtype: "numberfield",
                name: "paginas",
                maxLenght: 255,
                fieldLabel: "Página",
            });
            items.push({
                width: width,
                allowBlank: false,
                xtype: "textfield",
                name: "volume",
                maxLenght: 255,
                fieldLabel: "Volume",
                value: 'I',
                // regex: "^[a-zA-Z_]*$",
                regex: /^[mdclxviMDCLXVI]*$/,
                regexText: "<b>Erro:</b></br>Favor utilizar algarismos romanos.",
                validator: function(v) {
                    return /^[mdclxviMDCLXVI]*$/.test(v)?true:"Favor utilizar algarismos romanos";
                }
            });
            items.push({
                width: width,
                name: "protocolo_externo",
                fieldLabel: "P. Externo",
                xtype: "textfield",
            });
            items.push({
                name: "sigiloso",
                fieldLabel: "Sigiloso",
                xtype: "checkbox",
            });
            items.push(new Ext.Panel({
                layout: 'form',
                labelAlign: "top",
                border: false,
                items:[
                    new toolkit.plugins.CKEditor({
                        name: 'resumo',
                        fieldLabel: 'Corpo texto (4000 caracteres)',
                        autoScroll: true,
                        height: 145
                    })
                ]
            }));

            return items;
        },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Salvar rascunho',
                    scope: this,
                    handler: this.save,
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];
        }

        return this._buttons;
    },

    processMatter: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._ProcessMatter = value;

            if(dispatch) this.observeProcessMatter();
        }

        return this._ProcessMatter;
    },

    observeProcessMatter: function() {
        var value = this.processMatter();

        if(value) {
            this.getProcessMatterGrid().enable();
            this.getProcessMatterGrid().setParam('process', value, 101);
            this.getProcessMatterGrid().setFilterProperty('process', value, 101);

            this.getInterestedM2MField().objectId(value);
            this.getInterestedPanel().enable();

            this.getAttachmentGrid().enable();
            this.getAttachmentGrid().setParam('protocol', value, 101);
            this.getAttachmentGrid().setParam('moviment', this.values.movimentacao, 101);
            this.getAttachmentGrid().setFilterProperty('protocol', value, 101);

            this.getReferenciasGrid().enable();
            this.getReferenciasGrid().setParam('processo', value, 101);
            this.getReferenciasGrid().setFilterProperty('processo', value, 101);
        } else {
            this.getProcessMatterGrid().disable();
            this.getProcessMatterGrid().setParam('process', 0, 101, false);
            this.getProcessMatterGrid().setFilterProperty('process', 0, 101, false);

            this.getInterestedPanel().disable();

            this.getAttachmentGrid().disable();
            this.getAttachmentGrid().setParam('protocol', 0, 101, false);
            this.getAttachmentGrid().setParam('moviment', 0, 101, false);
            this.getAttachmentGrid().setFilterProperty('protocol', 0, 101, false);

            this.getReferenciasGrid().disable();
            this.getReferenciasGrid().setParam('processo', 0, 101);
            this.getReferenciasGrid().setFilterProperty('processo', 0, 101, true);
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.values = core.nullValue(cfg.values, {});
        this.action = cfg.action;
        this.values.started = true;

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.values.codigo = instance.codigo;
                    this.values.movimentacao = instance.primeira_movimentacao;
                    this.values.status = {encaminhado: false, finalizado: false, recebido: true};
                    this.getReferenciasGrid().setFilterProperty('processo', instance.pk);
                    this.getReferenciasGrid().setParam('processo', instance.pk);
                    this.getReferenciasGrid().enable();

                    this.processMatter(instance.pk);
                }
            }
        });

        edocs.processo.admin.processoAdminWindow.superclass.constructor.call(this, cfg);

        this.observeProcessMatter();

        if (this.action == 'update') {
            this.getReferenciasGrid().setFilterProperty('processo', this.oId);
            this.getReferenciasGrid().setParam('processo', this.oId);
            this.getReferenciasGrid().enable();

            this.processMatter(this.oId);
        }
    },
});
