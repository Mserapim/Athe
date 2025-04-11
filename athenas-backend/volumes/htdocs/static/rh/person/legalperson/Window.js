Ext._define('rh.person.legalperson.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.person.legalperson.Restful',
    width: 760,
    height: 700,

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.legalPerson(instance.pk);

                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        rh.person.legalperson.Window.superclass.constructor.call(this, cfg);

        this.legalPerson(cfg.oId === undefined ? null : cfg.oId);
    },

    legalPerson: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._legalPerson = value;

            !prevent && this.observeLegalPerson();
        }

        return this._legalPerson;
    },

    observeLegalPerson: function() {
        value = this.legalPerson();

        if(value) {

            this.getAddressGrid().enable();
            this.getAddressGrid().setParam('person', value);
            this.getAddressGrid().setFilterProperty('person', value, 100);

            this.getPhoneGrid().enable();
            this.getPhoneGrid().setParam('person', value);
            this.getPhoneGrid().setFilterProperty('person', value, 100);

            this.getAttachmentsGrid().enable();
            this.getAttachmentsGrid().setParam('person', value);
            this.getAttachmentsGrid().setFilterProperty('person__id', value, 100);

        } else {
            this.getAddressGrid().disable();
            this.getAddressGrid().setParam('person', 0);
            this.getAddressGrid().setFilterProperty('person', 0, 100, false);

            this.getPhoneGrid().disable();
            this.getPhoneGrid().setParam('person', 0);
            this.getPhoneGrid().setFilterProperty('person', 0, 100, false);

            this.getAttachmentsGrid().disable();
            this.getAttachmentsGrid().setParam('person', 0);
            this.getAttachmentsGrid().setFilterProperty('person__id', 0, 100, false);
        }

    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        tabPosition: 'top',
                        border: false,
                        items: [
                            this.getTabMain(cfg),
                            this.getTabAttachments(cfg)
                        ]
                    })
                ]
            });

        return this._formPanel;
    },

    getTabMain: function(cfg) {
        if(!this._tabMain)
            this._tabMain = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Principal',
                iconCls: 'icon-rh icon-core-main-tab',
                border: false,
                frame: true,
                scope: this,
                height: 665,
                items: [
                   {
                       maxLength: 100,
                       allowBlank: false,
                       fieldLabel: 'Nome Fantasia *',
                       name: 'nome',
                       xtype: 'textfield',
                       width: 400
                   },
                   {
                       maxLength: 14,
                       allowBlank: true,
                       fieldLabel: 'CNPJ',
                       name: 'cnpj',
                       xtype: 'textfield',
                       width: 400
                   },
                   {
                       maxLength: 255,
                       allowBlank: false,
                       fieldLabel: 'Razão Social *',
                       name: 'razao_social',
                       xtype: 'textfield',
                       width: 400
                   },
                   {
                       maxLength: 255,
                       allowBlank: true,
                       fieldLabel: 'Email',
                       name: 'email',
                       xtype: 'textfield',
                       width: 400
                   },
                   {
                      xtype: 'checkbox',
                      fieldLabel: 'Habilita Protocolo',
                      allowBlank: true,
                      name: 'enable_protocol'
                   },
                   {
                       layout: 'form',
                       border: false,
                       padding : '15px 0',
                       autoHeight: true,
                       items: [
                           this.getAddressGrid(cfg)
                       ]
                   },
                   {
                       layout: 'form',
                       border: false,
                       padding : '15px 0',
                       autoHeight: true,
                       items: [
                           this.getPhoneGrid(),
                       ]
                   }
                ]
            });
        return this._tabMain;
    },

    getTabAttachments: function(cfg) {
        if(!this._tabAttachments)
            this._tabAttachments = Ext._create('Ext.Panel', {
                layout: 'form',
                title: 'Anexos',
                iconCls: 'icon-rh icon-core-contacts-tab',
                border: false,
                frame: true,
                scope: this,
                autoHeight: true,
                items: [
                    this.getAttachmentsGrid(cfg)
                ]
            });
        return this._tabAttachments;
    },

    getAddressGrid: function(cfg) {
        if(!this._addressGrid) {
            this._addressGrid = Ext._create('rh.endereco.EnderecoGrid',{
                hideItemsToolbar: ['search', 'download'],
                title: 'Endereço',
                region: 'center',
                border: false,
                frame: true,
                scope: this,
                height: 200,
                columnAction: false,
            });
        }
        return this._addressGrid;
    },

    getPhoneGrid: function(cfg) {
        if(!this._phoneGrid) {
            this._phoneGrid = Ext._create('rh.telefone.TelefoneGrid',{
                hideItemsToolbar: ['search', 'download'],
                title: 'Telefones',
                region: 'center',
                border: false,
                frame: true,
                scope: this,
                height: 260,
                columnAction: false,
            });
        }
        return this._phoneGrid;
    },

    getAttachmentsGrid: function (cfg) {
        if (!this._attachments) {
            this._attachments = Ext._create('rh.digitaldocument.person.Grid', {
                hideItemsToolbar: ['search', 'download'],
                region: 'center',
                scope: this,
                frame: true,
                width: 730,
                height: 600,
                gridAutoLoad: false,
            });
        }
        return this._attachments;
    }

});

rh.person.Grid.register(
    'pessoajuridica',
    'Pessoa Jurídica',
    'icon-rh icon-core-legal-person',
    'rh.person.legalperson.Window'
);
