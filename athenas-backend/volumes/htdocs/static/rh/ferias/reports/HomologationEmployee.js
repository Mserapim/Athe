/**
 *
 **/

Ext._define('rh.ferias.reports.HomologationEmployee', {
    extend: 'toolkit.widget.TabPanel',

    _buildReport: function (paycheck) {
        var message = 'Preencha todos os campos do formulário.';
        var valid = true;

        if (this.getPeriodoAquisitivo().getValue() == undefined) {
            message = 'Preencha o Período Aquisitivo.';
            valid = false;
        } else if (this.getPeriodoAquisitivo().getValue()) {
            var periodo_arquisitivo_id = this.getPeriodoAquisitivo().getValue();

            var values = this.getPeriodoAquisitivo().getComboField().getStore().getById(periodo_arquisitivo_id).data;

            // if(values.data_publicacao == undefined){
            //     valid = false;
            //     message = 'O Período Aquisitivo não possui data de publicação.';
            // }
            if (values.ano_aquisicao == undefined) {
                message = 'O Período Aquisitivo não possui ano de aquisição.';
                valid = false;
            }
        }

        if (this.getAtoField().getValue() == undefined) {
            message = 'Preencha o ATO.';
            valid = false;
        }

        if (this.getOrdenacao().getValue() == undefined) {
            message = 'Preencha a Ordenação.';
            valid = false;
        }

        if (valid == true) {
            var periodo_arquisitivo_id = this.getPeriodoAquisitivo().getValue();
            var ato = this.getAtoField().getValue();
            var ordenacao = this.getOrdenacao().getValue();
            var values = this.getPeriodoAquisitivo().getComboField().getStore().getById(periodo_arquisitivo_id).data;

            if (values.data_publicacao != undefined) {
                var data = values.data_publicacao.toLocaleString().substr(0, 9)
            } else {
                var data = new Date().dateFormat("d/M/Y h:m:s");
            }

            var ano = values.ano_aquisicao;
            var tipo_relatorio = values.data_homologacao_prev > Date() ? 0 : 1;

            engine.mq.Report.request(
                {
                    report: '/to/mpe/rh/ferias/Ato_Homologacao_Servidores',
                    waitMessage: 'Gerando relatório...',
                    params: {
                        outfile: 'feriashomologacaoservidores',
                        report_name: 'Férias - Homologação Servidores',
                        ato: ato,
                        data: data,
                        periodo_arquisitivo_id: periodo_arquisitivo_id,
                        ordenacao: ordenacao,
                        tipo_relatorio: tipo_relatorio,
                        ano: ano,
                    },
                },
                this.getComboFieldOutputFormat().getValue()
            );
        } else Ext.Msg.show({
            msg: message,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        });
    },

    getPeriodoAquisitivo: function () {
        if (!this._periodoaquisitivo)
            this._periodoaquisitivo = Ext._create('core.fields.AutocompleteField', {
                name: 'periodoaquisitivo',
                rest: 'rh.ferias.pas.AcquisitionPeriodRestful',
                fieldLabel: 'Periodo Aquisitivo',
                width: 350,
                preFilter: [{ 'property': 'configuracao__modo', 'value': 'CONTINUO', 'stage': 1000 }],
            });

        return this._periodoaquisitivo;
    },

    getAtoField: function () {
        if (!this._atofield)
            this._atofield = Ext._create('Ext.form.TextField', {
                fieldLabel: 'ATO n°',
                name: 'portaria',
                width: 350,
            });

        return this._atofield;
    },

    getOrdenacao: function () {
        if (!this._classe) {
            this._classe = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Ordenação',
                hiddenName: 'ordenacao',
                width: 350,
                triggerAction: 'all',
                allowBlank: false,
                store: [
                    [1, 'Alfabética'],
                    [2, 'Cronológica'],
                ],
            });
        }

        return this._classe;
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
                                title: 'Portaria de Homologação - Servidores',
                                name: 'fieldServidor',
                                width: 500,
                                style: 'margin: 5px',
                                align: 'center',
                                items: [
                                    this.getPeriodoAquisitivo(),
                                    this.getAtoField(),
                                    this.getOrdenacao(),
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
                                    },
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
                title: 'Relatório -> Férias Homologação - Servidores'
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

        rh.ferias.reports.HomologationEmployee.superclass.constructor.call(this, cfg);
    }
});
