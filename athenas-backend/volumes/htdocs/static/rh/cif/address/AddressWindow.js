Ext._define('cif.address.AddressWindow', {
    extend: 'core.RestfulWindow',

    rest: 'cif.address.AddressRestful',

    width: 600,

    workplaceField: function() {
        if (!this._workplaceField)
            this._workplaceField = Ext._create('Ext.form.TextField', {
                name: "workplace",
                fieldLabel: "workplace",
                width: 450,
                hidden: true,
            });

        return this._workplaceField;
    },

    getFormPanel: function(cfg) {

        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    xtype: "rest-autocompletefield",
                    width: 450,
                    fieldLabel: "Período de Referência",
                    allowBlank: false,
                    rest: "cif.referenceperiod.ReferencePeriodRestful",
                    name: "refperiod_address",
                },
                this.getEndereco(cfg),
                {
                    xtype: "rest-autocompletefield",
                    hidden:true,
                    width: 450,
                    fieldLabel: "Member",
                    allowBlank: false,
                    rest: "cif.controlinformationmember.ControlInformationMemberRestful",
                    name: "member",
                },
                this.workplaceField(),
                {
                    allowBlank: false,
                    width: 450,
                    fieldLabel: "Data In\u00edcio Resid\u00eancia",
                    name: "start_date",
                    xtype: "datefield"
                },


                this.getAuthorizationField(),

                {
                    xtype: "combo",
                    width: 450,
                    fieldLabel: "Tipo de Resid\u00eancia",
                    allowBlank: false,
                    lazyRender: true,
                    hiddenName: "type_residence",
                    mode: "local",
                    triggerAction: "all",
                    store: [
                        [1, "CASA"],
                        [2, "APARTAMENTO"],
                        [3, "HOTEL"]
                    ],
                    name: "type_residence"
                },

                // {
                //     xtype: "ged-fileuploadfield",
                //     width: 450,
                //     fieldLabel: "Anexo",
                //     allowBlank: true,
                //     name: "file_document"
                // },

            ]
            });

        return this._formPanel;
    },

    getEndereco: function(cfg){
        this.person_id = (cfg.params != undefined ? cfg.params.person : 0)

        // cfg = core.nullValue(cfg, {});
        // Ext.applyIf(cfg, {params: {}});
        // this.person_id = cfg.values.person;

        if (!this._endereco){
            this._endereco = Ext._create('core.fields.AutocompleteField',{
                    xtype: "rest-autocompletefield",
                    width: 450,
                    fieldLabel: "Endereço",
                    allowBlank: false,
                    rest: "rh.endereco.EnderecoRestful",
                    name: "ref_address",
                });
                this._endereco.gridConfig = {params: {person: this.person_id}};

                this._endereco.setPreFilter([{
                    property: 'person__id',
                    value: this.person_id,
                    stage: 0,
                }]);
        }

        return this._endereco;
    },

    getAuthorizationField: function() {
        if (!this._authorizationField)
            this._authorizationField = Ext._create('Ext.form.Checkbox', {
                name: 'authorization_reside_outside',
                fieldLabel: "Autorização",
                boxLabel: 'Possui autorização do Conselho para residir fora da Comarca?',
            });

        return this._authorizationField;
    },

    _manipular: function(combo, record, index) {
        if(record.data.pk != this.workplaceField().value) {
            this.getAuthorizationField().enable();
        }
        else {
            this.getAuthorizationField().disable();
            this.getAuthorizationField().setValue(false);
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                disableSaveAndNew: true,
            }
        );

        Ext.apply(
            cfg,
            {
                items: [
                    this.getFormPanel(cfg)
                ]
            }
        );

        cif.address.AddressWindow.superclass.constructor.call(this, cfg);
    }
});
