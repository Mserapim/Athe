/**
 *
 **/

Ext._define('rh.ferias.reports.HomologationMembros', {
    extend: 'toolkit.widget.TabPanel',

    _buildReport: function (paycheck) {

        var valid = true;
        var periodo_arquisitivo_id = undefined;
        var portaria = undefined;
        var data = undefined;
        var ano = undefined;
        var tipo_membro = undefined;
        var tipo_relatorio = undefined;

        if (!this.getPortariaField().getValue()) {
            valid = false;
            message = 'Portaria não informada.'
        }
        if (!this.getPeriodoAquisitivo().getValue()) {
            valid = false;
            message = 'Período aquisitivo não informado.'
        } else {
            periodo_arquisitivo_id = this.getPeriodoAquisitivo().getValue();
            var values = this.getPeriodoAquisitivo().getComboField().getStore().getById(periodo_arquisitivo_id).data;
            if (!values.data_publicacao) {
                valid = false;
                message = 'Data de publicação não preenchida.'
            } else {
                data = values.data_publicacao.toLocaleString().substr(0, 9);
            }
            if (!values.ano_aquisicao) {
                valid = false;
                message = 'Data de publicação não preenchida.'
            } else {
                ano = values.ano_aquisicao;
            }
        }
        if (!this.getClasse().getValue()) {
            valid = false;
            message = 'Classe não informada.'
        } else {
            tipo_membro = this.getClasse().getValue();
        }
        if (!this.getProvisorio().getValue()) {
            valid = false;
            message = 'Provisório não informado.'
        } else {
            tipo_relatorio = this.getProvisorio().getValue();
        }

        if (valid) {
            engine.mq.Report.request(
                {
                    report: '/to/mpe/rh/ferias/Portaria_Homologacao_Membros',
                    waitMessage: 'Gerando relatório...',
                    params: {
                        outfile: 'feriashomologacaomembros',
                        report_name: 'Férias - Homologação Membros',
                        portaria: portaria,
                        data: data,
                        tipo_membro: tipo_membro,
                        tipo_relatorio: tipo_relatorio,
                        ano: ano,
                    }
                },
                this.getComboFieldOutputFormat().getValue()
            );
        } else Ext.Msg.show({
            msg: message,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

    getComboFieldOutputFormat: function () {
        if (!this._comboFieldOutputFormat) {
            this._comboFieldOutputFormat = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Formato',
                hiddenName: 'outputformat',
                width: 350,
                triggerAction: 'all',
                allowBlank: false,
                store: [
                    ['PDF', 'PDF'],
                    ['XLS', 'XLS'],
                    ['ODT', 'ODT'],
                ],
                value: 'PDF'
            });
        }
        return this._comboFieldOutputFormat;
    },

    getPeriodoAquisitivo: function () {
        if (!this._periodoaquisitivo)
            this._periodoaquisitivo = Ext._create('core.fields.AutocompleteField', {
                name: 'periodoaquisitivo',
                rest: 'rh.ferias.pas.AcquisitionPeriodRestful',
                fieldLabel: 'Periodo Aquisitivo',
                width: 350,
                preFilter: [{ 'property': 'configuracao__modo', 'value': 'ANUAL', 'stage': 1000 }],
            });

        return this._periodoaquisitivo;
    },

    getPortariaField: function () {
        if (!this._portariafield)
            this._portariafield = Ext._create('Ext.form.TextField', {
                fieldLabel: 'PORTARIA n°',
                name: 'portaria',
                width: 350,
            });

        return this._portariafield;
    },

    getClasse: function () {
        if (!this._classe) {
            this._classe = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Classe',
                hiddenName: 'classe',
                width: 350,
                triggerAction: 'all',
                allowBlank: false,
                store: [
                    [1, 'Promotores'],
                    [2, 'Procuradores'],
                    [3, 'Todos']
                ],
            });
        }

        return this._classe;
    },

    getProvisorio: function () {
        if (!this._provisorio) {
            this._provisorio = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Provisorio',
                hiddenName: 'provisorio',
                width: 350,
                triggerAction: 'all',
                allowBlank: false,
                store: [
                    [1, 'Sim'],
                    [2, 'Não'],
                ],
            });
        }

        return this._provisorio;
    },


    getMain: function () {
        if (!this._panel)
            this._panel = new Ext.Panel({
                layout: 'border',
                region: 'center',
                height: 650,
                split: true,
                autoEl: { tag: 'center' },
                items: [
                    {
                        region: 'center',
                        border: false,
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Portaria de Homologação - Membros',
                                name: 'fieldServidor',
                                width: 500,
                                style: 'margin: 5px',
                                align: 'center',
                                items: [
                                    this.getPeriodoAquisitivo(),
                                    this.getPortariaField(),
                                    this.getClasse(),
                                    this.getProvisorio(),
                                    this.getComboFieldOutputFormat(),
                                    {
                                        xtype: 'button',
                                        iconCls: 'icon-siatu icon-siatu-move-down',
                                        style: 'margin-top: 10px',
                                        text: 'Gerar Relatório',
                                        width: 100,
                                        height: 25,
                                        scope: this,
                                        handler: this._buildReport,
                                    },
                                    {
                                        xtype: 'displayfield',
                                        value: '* Deixe os campos em branco para selecionar Todos',
                                        hideLabel: true,
                                    }
                                ]
                            },
                        ]
                    }
                ]
            });

        return this._panel;
    },




    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Férias Homologação - Membros'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getMain(),
                ]
            }
        );

        rh.ferias.reports.HomologationMembros.superclass.constructor.call(this, cfg);
    }
});
