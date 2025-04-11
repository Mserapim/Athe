Ext._define('rh.publicacao.PublicationGeneralWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.publicacao.Restful',

    width: 820,


    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [{
                    xtype: 'tabpanel',
                    height: 420,
                    activeItem: 0,
                    border: false,
                    items: [
                        this.getPublicacaoPanel(),
                        this.getDocumentPanel(),
                        // this.getPublicacaoAnexo(),
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

    // getPublicacaoAnexo: function(cfg) {
    //     if(!this._publicacaoAnexo)
    //         this._publicacaoAnexo = Ext._create('Ext.Panel', {
    //             title: 'Anexo(s)',
    //             layout: {
    //                 type: 'hbox',
    //                 align: 'stretch'
    //             },
    //             items: [
    //                 {
    //                     xtype: 'ckeditor',
    //                     name: 'observacao',
    //                     height: 283
    //                 }
    //             ]
    //         });

    //     return this._publicacaoAnexo;
    // },

    // getPublicacaoAnexo: function() {
    //         if(!this._gedGrid)
    //             this._gedGrid = new adm.daily.ged.Grid({
    //                 title: 'Anexo(s)',
    //                 layout: 'fit'
    //             });
// 
    //         return this._gedGrid;
    //     },

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
                    },

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

        rh.publicacao.PublicationGeneralWindow.superclass.constructor.call(this, cfg);
        if((cfg.values || {}).document_read_only !== undefined)
            this.documentReadOnly(cfg.values.document_read_only);
    }

});
