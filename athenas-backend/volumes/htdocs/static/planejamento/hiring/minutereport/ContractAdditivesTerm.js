Ext._define('planning.hiring.minutereport.ContractAdditivesTerm', {
    extend: 'toolkit.widget.TabPanel',

    getExpirationFrom: function() {
        if (!this._expirationFrom)
            this._expirationFrom = Ext._create('Ext.form.DateField', {
                name: 'expiration_from',
                fieldLabel: "Data Inicial",
                hidden: false,
                width: 350,
            });
        return this._expirationFrom;
    },

    getExpirationUntil: function() {
        if (!this._expirationUntil)
            this._expirationUntil = Ext._create('Ext.form.DateField', {
                name: 'expiration_until',
                fieldLabel: "Data Final",
                hidden: false,
                width: 350,
            });
        return this._expirationUntil;
    },


    getStatus: function() {
        if (!this._status) {
            this._status = Ext._create('Ext.form.ComboBox', {
                hiddenName: 'status',
                fieldLabel: 'Status',
                store: [
                    [0, 'TODOS'],
                    [100, 'ATIVO'],
                    [4, 'INATIVO'],
                ],
                allowBlank: false,
                triggerAction: 'all',
                width: 350,
            });
        }
        return this._status;
    },

    getFormPanel: function () {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                // frame: true,
                labelWidth: 100,
                autoHeight: true,
                width: 500,
                items: [
                    this.getExpirationFrom(),
                    this.getExpirationUntil(),
                    this.getStatus()
                ]
            });

        return this._formPanel;
    },

    getMain: function () {
        if (!this._panel)
            this._panel = Ext._create('Ext.Panel', {
                layout: 'border',
                region: 'center',
                height: 650,
                split: true,
                autoEl: { tag: 'center' },
                items: [
                    {
                        region: 'center',
                        border: false,
                        items:[
                            {
                                xtype: 'fieldset',
                                title: 'Termos Aditivos de Contratos',
                                width: 650,
                                style: 'margin: 5px',
                                align: 'left',
                                items: [
                                    this.getFormPanel(),
                                    {
                                        xtype: 'button',
                                        iconCls: 'icon-siatu icon-siatu-move-down',
                                        style: 'margin-top: 10px',
                                        text: 'Gerar Relatório',
                                        width: 100,
                                        height: 25,
                                        scope: this,
                                        menu: {
                                            scope: this,
                                            items: [
                                                {
                                                    text: 'Arquivo PDF ',
                                                    type: 'PDF',
                                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                                    scope: this,
                                                    handler: function (item) {
                                                        this.generate(item.type);
                                                    }
                                                },
                                                {
                                                    text: 'Arquivo ODT',
                                                    type: 'ODT',
                                                    iconCls: 'icon-ged icon-ged-application-msword',
                                                    scope: this,
                                                    handler: function (item) {
                                                        this.generate(item.type);
                                                    }
                                                },
                                                {
                                                    text: 'Arquivo XLS',
                                                    type: 'XLS',
                                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                    scope: this,
                                                    handler: function (item) {
                                                        this.generate(item.type);
                                                    }
                                                },
                                            ]
                                        },
                                    }
                                ]
                            },

                        ]
                    }
                ]
            });

        return this._panel;
    },


    generate: function (type) {

        expiration_from = this.getExpirationFrom().getValue();
        expiration_until = this.getExpirationUntil().getValue();
        status = this.getStatus().getValue();

        if(expiration_until < expiration_from){
            Ext.Msg.show({
                title: 'Atençao',
                msg: 'Data inicial maior que data final.',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK
            });
            return;
        }

        engine.mq.Report.request({
            report: '/to/mpe/planejamento/contrato/contract_additives_term',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'contract_additives_term',
                report_name: 'Termos de Aditivo de Contrato',
                expiration_from: Ext.util.Format.date(expiration_from, 'Y-m-d'),
                expiration_until: Ext.util.Format.date(expiration_until, 'Y-m-d'),
                status: status
            }
        }, type);
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Termos de Aditivo de Contrato',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:[
                    this.getMain(),
                ],
            }
        );

        planning.hiring.minutereport.ContractAdditivesTerm.superclass.constructor.call(this, cfg);
    }
});