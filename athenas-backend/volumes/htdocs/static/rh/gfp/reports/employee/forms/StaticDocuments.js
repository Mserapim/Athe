/*****************************************************************************
*                                                                            *
*                            OUTROS REQUERIMENTOS                            *
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.employee.forms.StaticDocuments', {
    extend: 'Ext.form.FormPanel',

    _populateCombo: function (files) {
        this.getDocumentField().getStore().add(files.map(function (file) {
            return Ext._create('Ext.data.Record', {
                title: file.title,
                url: file.url,
                //url: file.url.replace('127.0.0.1', 'athenas.mpto.mp.br'),  // debug
            });
        }));
    },

    _fetchFileUrls: function (cfg) {
        Ext.Ajax.request({
            method: 'GET',
            scope: this,
            url: window.action('services/cms/posts/json'),
            params: {
                start: 0, limit: 1,
                areas__parent__slug: 'intranet',
                areas__slug: 'requerimentos'
            },
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                try {
                    if (!result.list.length || !result.list[0].files.length) {
                        throw new Error('Requisição não retornou resultados');
                    }
                    this._populateCombo(result.list[0].files);
                } catch (e) {
                    this.getDocumentField().setValue('Erro ao carregar a lista');
                    throw e;
                }
            },
            failure: function (xhr) {
                Ext.Msg.show({
                    title: 'Outros requerimentos',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                });
            },
        });
    },

    _postConstructor: function (cfg) {
        this._fetchFileUrls(cfg);
    },

    getDocumentField: function (cfg) {
        if (this._documentField) {
            return this._documentField;
        }

        this._documentField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Documento',
            displayField: 'title',
            valueField: 'url',
            editable: false,
            triggerAction: 'all',
            anchor: '99%',
            mode: 'local',
            allowBlank: false,
            emptyText: 'Selecione um item...',
            submitValue: false,

            // OBS: store será populado no método _fetchFileUrls()
            store: Ext._create('Ext.data.ArrayStore', {
                fields: ['title', 'url'],
            }),
        });

        return this._documentField;
    },

    _validateFields: function (cfg) {
        if (this.getForm().isValid()) {
            return;
        }

        Ext.Msg.show({
            title: 'Validando',
            msg: 'Por favor, preencha os campos obrigatórios.',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK,
        });

        throw new Error('Por favor, preencha os campos obrigatórios.');
    },

    _generateButtonHandle: function (cfg) {
        this._validateFields(cfg);

        toolkit.util.downloadFile({
            url: this.getDocumentField().getValue(),
            filename: 'requerimento',
        });
    },

    getGenerateButton: function(cfg) {
        if (this._generateButton) {
            return this._generateButton;
        }

        this._generateButton = Ext._create('Ext.Button', {
            text: 'Gerar',
            scope: this,
            iconCls: 'icon-ged icon-ged-application-pdf',
            handler: function () {
                this._generateButtonHandle(cfg);
            },
        });

        return this._generateButton;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 70,
            items: this.getDocumentField(cfg),
            buttonAlign: 'left',
            buttons: [ this.getGenerateButton(cfg) ],
        });

        rh.gfp
          .reports
          .employee
          .forms
          .StaticDocuments
          .superclass
          .constructor
          .call(this, cfg);

        this._postConstructor(cfg);
    },
});
