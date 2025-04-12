Ext._define('rh.publicacao.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.publicacao.Restful',

    width: 820,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [{
                    xtype: 'tabpanel',
                    height: 760,
                    activeItem: 0,
                    border: false,
                    items: [
                        this.getPublicacaoPanel(),
                        // this.getPublicacaoSite(),
                        this.getDocumentPanel()
                    ]
                }]
            });


        return this._formPanel;
    },

    enablePublicacaoOficial: function(enabled){
        var form = this.getFormPanel().getForm();
        var numero_pub, data_pub;

        numero_pub = form.findField('numero_publicacao');
        data_pub = form.findField('data_publicacao');

        if(enabled) {
            numero_pub.enable();
            data_pub.enable();
        }
        else {
            numero_pub.disable();
            data_pub.disable();
        }
    },

    getPublicacaoSite: function(cfg) {
        if(!this._publicacaoSite)
            this._publicacaoSite = Ext._create('Ext.Panel', {
                title: 'Site',
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                items: [
                    {
                        xtype: 'ckeditor',
                        name: 'observacao',
                        height: 283
                    }
                ]
            });

        return this._publicacaoSite;
    },

    getDocumentField: function() {
        if(!this._documentField)
            this._documentField = Ext._create('toolkit.fields.CKEditor', {
                name: 'document',
                height: 283
            });

        return this._documentField;
    },

    getDocumentPanel: function(cfg) {
        if(!this._documentPanel)
            this._documentPanel = Ext._create('Ext.Panel', {
                title: 'Conteúdo do documento',
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                items: [
                    this.getDocumentField()
                ]
            });

        return this._documentPanel;
    },

    getPublicacaoPanel: function() {
        if(!this._eventPanel)
            this._eventPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                defaults: {
                    width: 680
                },
                title: 'Dados',
                layout: 'form',
                items: [
                    {
                        fieldLabel: 'Número',
                        xtype: 'textfield',
                        name: 'numero',
                        allowBlank: false
                    },{
                        fieldLabel: 'Tipo',
                        xtype: 'choicefield',
                        hiddenName: 'tipo',
                        choiceId: 'rh.TIPO_DOCUMENTO',
                        allowBlank: false,
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Origem',
                        allowBlank: false,
                        rest: 'rh.generalorgan.Restful',
                        name: 'origem'
                    },
                    {
                        fieldLabel: 'Expedição',
                        xtype: 'datefield',
                        name: 'data_expedicao',
                        allowBlank: false
                    },{
                        fieldLabel: 'Vigência',
                        xtype: 'datefield',
                        name: 'data_vigencia',
                        allowBlank: false
                    },{
                        fieldLabel: 'Interno',
                        xtype: 'checkbox',
                        name: 'interno',
                    },{
                        xtype:'fieldset',
                        title: 'Veículo de Publicação',
                        collapsible: false,
                        checkboxToggle: {
                            tag: 'input',
                            type: 'checkbox',
                            name: this.checkboxName || this.id+'-checkbox'
                        },
                        autoHeight: true,
                        width: 790,
                        defaults: {
                            width: 660
                        },
                        items :[
                            {
                                xtype: 'choicefield',
                                fieldLabel: 'Veiculo de Publicação',
                                hiddenName: 'veiculo_publicacao',
                                width: 550,
                                choiceId: 'rh.VEICULO_PUBLICACAO'
                            }, {
                                fieldLabel: 'Número',
                                xtype: 'textfield',
                                name: 'numero_publicacao',
                                allowBlank: true,
                                width: 200
                            }, {
                                fieldLabel: 'Publicado',
                                xtype: 'datefield',
                                name: 'data_publicacao',
                                allowBlank: true,
                                width: 100
                            }, {
                                fieldLabel: 'Página',
                                xtype: 'numberfield',
                                name: 'vehicle_page',
                                allowBlank: true,
                                width: 100
                            }
                        ]
                    },{
                        fieldLabel: 'Interessado',
                        xtype: 'textfield',
                        name: 'interessado_nome',
                        allowBlank: true,
                    },{
                        fieldLabel: 'Arquivo',
                        xtype: 'ged-fileuploadfield',
                        name: 'arquivo',
                        allowBlank: true,
                    },
                    {
                        fieldLabel: 'Site',
                        xtype: 'ckeditor',
                        name: 'observacao',
                        height: 200
                    }
                ]
            });

        return this._eventPanel;
    },

    documentReadOnly: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._documentReadOnly = value;

            if(dispatch)
                this.observeDocumentReadOnly();
        }

        return this._documentReadOnly;
    },

    observeDocumentReadOnly: function() {
        value = this.documentReadOnly();

        if(value) {
            this.getDocumentPanel().disable();
        }
        else {
            this.getDocumentPanel().enable();
        }
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            'disableSaveAndNew': true,
            'saveAndContinue': {
                'scope': this,
                'fn': function(instance) {
                    this.oId = instance.pk;
                    this.documentReadOnly(instance.document_read_only);
                    this.action = 'update';
                }
            }
        });

        rh.publicacao.Window.superclass.constructor.call(this, cfg);
        if((cfg.values || {}).document_read_only !== undefined)
            this.documentReadOnly(cfg.values.document_read_only);
    }

});
