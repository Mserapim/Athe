/**
 *
 **/

Ext._define('rh.registration.forminformation.Report', {
    extend: 'Ext.Window',

    width: 500,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 65,
                defaults: {
                    width: 400
                },
                items: [
                    this.getStateField(),
                    // this.getInitialDate(),
                    // this.getFinalDate(),
                    this.getDigitalDocumentTypeChoiceField(),
                    this.getEmployeeType()
                ]
            });
        return this._formPanel;
    },

    getInitialDate: function(){
        if(!this._startfield)
            this._startfield = Ext._create('Ext.form.DateField', {
                anchor: '100%',
                fieldLabel: 'Data Início',
                name: 'data_inicio',
                allowBlank: true,
                hidden: true
            });

        return this._startfield;
    },

    getFinalDate: function(){
        if(!this._endfield)
            this._endfield = Ext._create('Ext.form.DateField', {
                anchor: '100%',
                fieldLabel: 'Data Fim',
                name: 'data_fim',
                allowBlank: true,
                hidden: true
            });

        return this._endfield;
    },

    getStateField: function() {
        if (!this._stateField) {
            this._stateField = Ext._create('core.fields.ComboField', {
                fieldLabel: "Estado",
                hiddenName: "estado",
                allowBlank: false,
                displayField: 'description',
                store: [
                    [1, 'Recadastramento Funcional - Validados'],
                    [2, 'Recadastramento Funcional - Não Validados e/ou Com Pendências'],
                    [3, 'Comprovante Eleitoral - Validados'],
                    [4, 'Comprovante Eleitoral - Não Validados e/ou com Pendencias'],
                ],
                listeners: {
                    scope: this,
                    select: function(combo, record, index){
                        if(combo.value == 1 || combo.value == 2){
                            // this.getInitialDate().hide();
                            // this.getFinalDate().hide();
                            this.getDigitalDocumentTypeChoiceField().hide();
                        }
                        if(combo.value == 3 || combo.value == 4){
                            // this.getInitialDate().show();
                            // this.getFinalDate().show();
                            this.getDigitalDocumentTypeChoiceField().show();
                        }
                    }
                },
                autoLoad: true,
            });
        }

        return this._stateField;
    },

    getEmployeeType: function() {
        if (!this._employeeType) {
            this._employeeType = Ext._create('core.fields.ComboField', {
                fieldLabel: "Tipo",
                hiddenName: "type",
                allowBlank: false,
                displayField: 'description',
                store: [
                    ['S', 'Servidor'],
                    ['M', 'Membro'],
                ],
                autoLoad: true,
            });
        }

        return this._employeeType;
    },

    getDigitalDocumentTypeChoiceField: function(cfg) {
        if (!this._digitalDocumentTypeChoiceField){
            this._digitalDocumentTypeChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Tipo de Documento',
                hiddenName: 'document_type',
                choiceId: 'rh.DIGITAL_DOCUMENT_TYPE',
                hidden: true
            });
        }
        return this._digitalDocumentTypeChoiceField;
    },

    getValues: function() {
        return this.getFormPanel().getForm().getValues();
    },
    generate: function(preventClose, type) {

        if(this.getStateField().getValue()==1){
            var report = '/to/mpe/rh/registration/Validated';
            var _reportName = 'Recadastramento Funcional - Validados';
            var _reportFileName = 'relatorio_recadastramento_funcional_validados'
        }
        if(this.getStateField().getValue()==2){

            var report = '/to/mpe/rh/registration/Not_Validated_and_Validated_Pending';
            var _reportName = 'Recadastramento Funcional - Não Validados e Com Pendências';
            var _reportFileName = 'relatorio_recadastramento_funcional_nao_validados'
        }
        if(this.getStateField().getValue()==3){

            var report = '/to/mpe/rh/proof_voting/Validated';
            var _reportName = 'Comprovante Eleitoral - Validados';
            var _reportFileName = 'relatorio_comprovante_eleitoral_validados'
        }
        if(this.getStateField().getValue()==4){

            var report = '/to/mpe/rh/proof_voting/Not_Validated_and_Validated_Pending';
            var _reportName = 'Comprovante Eleitoral - Não Validados e/ou com Pendencias';
            var _reportFileName = 'relatorio_comprovante_eleitoral_nao_validados'
        }

        // inital_date = "";
        // final_date = "";
        // if(this.getStateField().getValue()==3 || this.getStateField().getValue()==4){
        //     inital_date = this.getInitialDate().getValue();
        //     final_date = this.getFinalDate().getValue();
        //     if(inital_date == undefined || inital_date == "" || final_date == undefined || final_date == ""){
        //         Ext.Msg.show({
        //             title: 'Aviso',
        //             icon: Ext.Msg.ERROR,
        //             buttons: Ext.Msg.OK,
        //             msg: 'Nessário preencher data inicial e data fim.'
        //         });
        //         return false;
        //     }else{
        //         inital_month = inital_date.getMonth() + 1 < 10 ? '0' + (inital_date.getMonth() + 1) : inital_date.getMonth() + 1;
        //         inital_day = inital_date.getDate() < 10 ? '0' + inital_date.getDate() : inital_date.getDate();
        //         final_month = final_date.getMonth() + 1 < 10 ? '0' + (final_date.getMonth() + 1) : final_date.getMonth() + 1;
        //         final_day = final_date.getDate() < 10 ? '0' + final_date.getDate() : final_date.getDate();

        //         inital_date = inital_date.getFullYear() + '-' + inital_month + '-' + inital_day;
        //         final_date = final_date.getFullYear() + '-' + final_month + '-' + final_day;
        //     }
        // }

        engine.mq.Report.request({
            report: report,
            params: Ext.apply(
                {
                    outfile: _reportFileName,
                    report_name: _reportName,
                    // data_inicial:  inital_date,
                    // data_final: final_date,
                    type_employee: this.getEmployeeType().getValue(),
                    digital_document_type: this.getDigitalDocumentTypeChoiceField().getValue(),
                }
            ),
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
        }, type);

        if(!preventClose) this.close();
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true,
                resizable: false,
                border: false
            }
        );

        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: [
                    {
                        text: 'Gerar',
                        scope: this,
                        // handler: function() { this.generate(false); }
                        menu: {
                            scope: this,
                            items: [
                                {
                                    text: 'Arquivo PDF ',
                                    type: 'PDF',
                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(false, item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo ODT',
                                    type: 'ODT',
                                    iconCls: 'icon-ged icon-ged-application-msword',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(false, item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo XLS',
                                    type: 'XLS',
                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(false, item.type);
                                    }
                                },
                            ]
                        },
                    },
                    {
                        text: 'Gerar e novo',
                        scope: this,
                        // handler: function() { this.generate(true); }
                        menu: {
                            scope: this,
                            items: [
                                {
                                    text: 'Arquivo PDF ',
                                    type: 'PDF',
                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(true, item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo ODT',
                                    type: 'ODT',
                                    iconCls: 'icon-ged icon-ged-application-msword',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(true, item.type);
                                    }
                                },
                                {
                                    text: 'Arquivo XLS',
                                    type: 'XLS',
                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                    scope: this,
                                    handler: function (item) {
                                        this.generate(true, item.type);
                                    }
                                },
                            ]
                        },
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        rh.gfp.transparencychoice.reports.Support.superclass.constructor.call(this, cfg);
    }
});
