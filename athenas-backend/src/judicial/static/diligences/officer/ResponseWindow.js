Ext._define('judicial.diligences.officer.ResponseWindow', {
    extend: 'core.RestfulWindow',

    rest: 'judicial.diligences.officer.ResponseRestful',

    width: 900,

    getResponsePanel: function(cfg) {
        if(!this._manifestationPanel)
            this._manifestationPanel = Ext._create('Ext.Panel', {
                title: 'Manifestação',
                border: false,
                frame: true,
                layout: 'form',
                items: [
                    {
                        fieldLabel: 'Diligência',
                        xtype: 'displayfield',
                        name: 'unicode',
                    },
                    {
                        fieldLabel: 'Pessoa',
                        xtype: 'displayfield',
                        name: 'who_unicode',
                    },
                    {
                        xtype: 'hidden',
                        name: 'diligence',
                    },
                    {
                        xtype: 'ckeditor',
                        name: 'text',
                        hideLabel: true,
                        height: 340
                    }
                ]
            });

        return this._manifestationPanel;
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                height: 550,
                items: [
                    this.getResponsePanel(),
                    this.getAttachedGrid()
                ]
            });

        return this._tabPanel;
    },

    getAttachedGrid: function() {
        if(!this._attachedGrid)
            this._attachedGrid = Ext._create('judicial.parts.AttachedGrid', {
                title: 'Anexos',
                gridAutoLoad: false
            });

        return this._attachedGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    this.getTabPanel()
                ]
            });

        return this._formPanel;
    },

    sign: function() {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {'msg': 'Processando...'});
        mask.show();
        rest.doRequest(
            rest.getRoute('sign', this.oId, 'PUT', {
                scope: this,
                callback: function(xhr) {
                    mask.hide();
                    this.destroy();
                },
                success: function(xhr) {
                    rst = Ext.decode(xhr.responseText);

                    if(rst.success){
                        Ext.Msg.show({
                            title: 'Assinando documento',
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: 'Documento assinado com sucesso.'
                        });
                    }else
                        Ext.Msg.show({
                            title: 'Assinando documento',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Assinando o documento',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'O sistema esta indisponível neste momento.'
                    });
                }
            })
        );
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Assinar',
                    scope: this,
                    handler: this.sign,
                    handle: this.sign
                },
                '->'
            ].concat(judicial.diligences.officer.ResponseWindow.superclass.getButtons.call(this, cfg));

        return this._buttons;
    },

    manifestation: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._manifestation = value;

            if(!prevent) this.observeResponse();
        }

        return this._manifestation;
    },

    observeResponse: function() {
        var value = this.manifestation();

        if(value) {
            this.getAttachedGrid().enable();
            this.getAttachedGrid().setParam('attached_response_officer', value);
            this.getAttachedGrid().setFilterProperty('attached_response_officer', value, 101);
        }
        else {
            this.getAttachedGrid().disable();
            this.getAttachedGrid().setParam('attached_response_officer', 0);
            this.getAttachedGrid().setFilterProperty('attached_response_officer', 0, 101);
        }
    },

    getResponseOfficer: function(diligence){
        var rest = this.factoryRestful();
        rest.doRequest(
            rest.getRoute('get_by_diligence', diligence.pk, 'GET', {
                scope: this,
                success: function(xhr) {
                    rst = Ext.decode(xhr.responseText);

                    if(rst.success){
                        this.getFormPanel().getForm().setValues(rst.instance);
                        this.oId = rst.instance.pk;
                        this.action = 'update';
                        this.manifestation(rst.instance.pk);
                    }
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Falha',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'O sistema esta indisponível neste momento.'
                    });
                }
            })
        );

    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Manifestação em Diligência Interna',
            border: false,
            buttonAlign: 'left',
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.manifestation(instance.pk);
                }
            }
        });

        judicial.diligences.officer.ResponseWindow.superclass.constructor.call(this, cfg);
        this.manifestation(this.oId || null);
        this.getResponseOfficer(this.values);
    }
});