
Ext.ns('toolkit.gfp');

Ext.apply(
    toolkit.widget,
    {
        CommanderController: Ext.extend(
            Ext.Window,
            {
                controller: null,

                getDownloadUrl: function (obj) {
                    return toolkit.util.Normalize.controller_action(
                        this.controller,
                        'getFile'
                    ) + '?sid=' + obj.sid;
                },

                destroy: function () {
                    if (this.task) Ext.TaskMgr.stop(this.task);

                    toolkit.widget.CommanderController.superclass.destroy.call(this);
                },

                start: function () {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(this.controller, 'createSessionId'),
                        params: this.getFormPanel().getForm().getValues(),
                        success: function (request) {
                            var obj = Ext.decode(request.responseText);
                            this.processSession(obj);
                        },
                        failure: function (request) {
                            Ext.Msg.show({
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: 'Ocorreu um erro, tente novamente mais tarde.'
                            })
                        },
                        scope: this
                    })
                },
                //                #TODO  Retirar a chamada this.update e caso necessite sobrescrever, utilizar o método updateProgress
                updateInfoProgress: function (obj) {
                    this.getProgressBar().updateProgress(obj.pct, obj.pctText, true);
                },

                upgradeProgress: function (sid) {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            'getSessionInformation'
                        ),
                        params: {
                            sid: sid
                        },
                        success: function (request) {
                            var obj = Ext.decode(request.responseText);

                            if (obj.done && !obj.error) {
                                var url = this.getDownloadUrl(obj)

                                var width = 235;
                                var height = 175;
                                var left = (screen.width - width) / 2;
                                var top = (screen.height - height) / 2;

                                window.open(
                                    url,
                                    'buildFile',
                                    'status=no, width=' + width + ', height=' + height + ', toolbar=no, resizable=no, left=' + left + ', top=' + top
                                );

                                Ext.TaskMgr.stop(this.task);

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        this.controller,
                                        'destroySession'
                                    ),
                                    params: { sid: obj.sid }
                                });
                            }
                            else if (obj.error) {

                                Ext.TaskMgr.stop(this.task);
                                alert(obj.error);

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        this.controller,
                                        'destroySession'
                                    ),
                                    params: { sid: obj.sid }
                                });

                            }

                            this.updateInfoProgress(obj);
                        },
                        scope: this
                    });
                },

                processSession: function (obj) {
                    this.task = Ext.TaskMgr.start({
                        interval: (5 * 1000),
                        run: this.upgradeProgress,
                        scope: this,
                        args: [obj.sid]
                    });

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            'start'
                        ),
                        params: {
                            sid: obj.sid
                        },
                        scope: this
                    });
                }
            }
        )
    }
);


toolkit.gfp.WindowTaskCommandController = Ext.extend(
    Ext.Window,
    {
        getItemsForm: function (cfg) {
            return [];
        },

        getFormPanel: function (cfg) {
            if (!this.formPanel)
                this.formPanel = new Ext.form.FormPanel({
                    items: this.getItemsForm(cfg),
                });

            return this.formPanel;
        },

        execute: function () {
            var form = this.getFormPanel().getForm();

            form.waitMsgTarget = this.getFormPanel().getEl();
            console.debug(this.params);
            form.submit({
                url: toolkit.util.Normalize.controller_action(this.controller, this.action),
                params: this.params,
                failure: function (form, action) {
                    console.debug(action);
                },
                success: function (form, action) {
                    console.debug(this.params);
                    console.debug('SUCCESS...');
                    this.close();
                },
                scope: this,
                waitMsg: 'Aguarde ...'
            });
        },

        constructor: function (cfg) {
            if (!cfg) cfg = {}

            Ext.applyIf(
                cfg,
                {
                    title: 'Task Window',
                    closable: true,
                    resizable: false,
                    width: 800,
                    border: false,
                    modal: true,
                    controller: '',
                    action: 'generate_file',
                    items: [
                        this.getFormPanel(cfg),
                    ],
                    buttons: [
                        {
                            text: 'Executar',
                            scope: this,
                            handler: this.execute
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                }
            );

            toolkit.gfp.WindowTaskCommandController.superclass.constructor.call(this, cfg);
        }
    }
);


toolkit.gfp.FileGerenatorRAISGFP = Ext.extend(
    toolkit.gfp.WindowTaskCommandController,
    {
        getItemsForm: function (cfg) {
            return [
                {
                    name: 'ano_base',
                    xtype: 'numberfield',
                    fieldLabel: 'Ano base',
                    value: (new Date().getFullYear() - 1)
                },
                {
                    name: 'retificadora',
                    xtype: 'checkbox',
                    fieldLabel: 'Retificadora',
                    checked: false
                }
            ]
        }
    }
);

toolkit.gfp.FileGeneratorReturnPeriodGFP = Ext.extend(
    toolkit.gfp.WindowTaskCommandController,
    {
        getItemsForm: function (cfg) {
            return [
                {
                    xtype: 'rest-autocompletefield',
                    fieldLabel: 'Período',
                    name: 'period',
                    rest: 'rh.gfp.payroll.PeriodRestful',
                    value: (cfg && cfg.period ? cfg.period.pk : ''),
                    allowBlank: false,
                },
            ]
        },

    }
);

toolkit.gfp.FileGeneratorReturnPayrollGFP = Ext.extend(
    toolkit.gfp.WindowTaskCommandController,
    {
        getItemsForm: function (cfg) {
            return [
                {
                    xtype: 'rest-autocompletefield',
                    fieldLabel: 'Folha',
                    name: 'payroll',
                    rest: 'rh.gfp.payroll.PayrollRestful',
                    value: (cfg && cfg.payroll ? cfg.payroll.pk : ''),
                    allowBlank: false,
                },
            ]
        },
        execute: function () {
            var form = this.getFormPanel().getForm();

            form.waitMsgTarget = this.getFormPanel().getEl();
            console.debug(this.params);
            form.submit({
                url: toolkit.util.Normalize.controller_action(this.controller, this.action),
                params: this.params,
                failure: function (form, action) {
                    if (!action.result.sucess) {
                        Ext.Msg.show({
                            title: 'Alerta',
                            msg: action.result.message,
                            buttons: Ext.Msg.OK,
                            icon: Ext.MessageBox.WARNING
                        });
                    }
                },
                success: function (form, action) {
                    if (!action.result.sucess) {
                        Ext.Msg.show({
                            title: 'Sucesso',
                            msg: 'O processo começou. Você será avisado quando terminar.',
                            buttons: Ext.Msg.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }
                },
                scope: this,
                waitMsg: 'Aguarde ...'
            });
        },
    }
);

toolkit.gfp.CarregarProcessosRRAGFP = Ext.extend(
    toolkit.gfp.WindowTaskCommandController,
    {
        getItemsForm: function (cfg) {
            return [
                {
                    xtype: 'rest-autocompletefield',
                    fieldLabel: 'Processos RRA',
                    name: 'rra',
                    rest: 'rh.gfp.parameters.RRARestful',
                    allowBlank: false,
                },
            ]
        },
        execute: function (cfg) {
            var form = this.getFormPanel().getForm();
            this.params = {"folha":this.payroll.pk}
            form.waitMsgTarget = this.getFormPanel().getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action(this.controller, this.action),
                params: this.params,
                failure: function (form, action) {
                    if (!action.result.sucess) {
                        Ext.Msg.show({
                            title: 'Alerta',
                            msg: action.result.message,
                            buttons: Ext.Msg.OK,
                            icon: Ext.MessageBox.WARNING
                        });
                    }
                },
                success: function (form, action) {
                    if (!action.result.sucess) {
                        Ext.Msg.show({
                            title: 'Sucesso',
                            msg: 'O processo começou. Você será avisado quando terminar.',
                            buttons: Ext.Msg.OK,
                            icon: Ext.MessageBox.INFO
                        });
                    }
                },
                scope: this,
                waitMsg: 'Aguarde ...'
            });
        },
    }
);

Ext.apply(
    toolkit.gfp,
    {
        ModeloFolha: Ext.extend(
            Ext.Window,
            {
                controller: 'GFPControlador',

                start: function () {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(this.controller, 'apply_model'),
                        params: this.getFormPanel().getForm().getValues(),
                        success: function (request) {
                            var obj = Ext.decode(request.responseText);
                            this.destroy();
                            // this.processSession(obj);
                        },
                        failure: function (request) {
                            Ext.Msg.show({
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: 'Ocorreu um erro, tente novamente mais tarde.'
                            })
                        },
                        scope: this
                    })
                },

                getDownloadUrl: function (obj) {
                    return toolkit.util.Normalize.controller_action(
                        this.controller,
                        'getFile'
                    ) + '?sid=' + obj.sid +
                        '&folha_tipo=' + obj.folha_tipo +
                        '&folha_mes=' + obj.folha_mes +
                        '&folha_ano=' + obj.folha_ano +
                        '&banco=' + obj.banco;
                },

                upgradeProgress: function (sid) {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            'getSessionInformation'
                        ),
                        params: {
                            sid: sid
                        },
                        success: function (request) {
                            var obj = Ext.decode(request.responseText);

                            if (obj.done && !obj.error) {
                                Ext.Msg.show({
                                    msg: 'Processo finalizado com sucesso.',
                                    icon: Ext.Msg.INFORMATION,
                                    buttons: Ext.Msg.OK
                                });

                                Ext.TaskMgr.stop(this.task);

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        this.controller,
                                        'destroySession'
                                    ),
                                    params: { sid: obj.sid }
                                });
                            }
                            else if (obj.error) {

                                Ext.TaskMgr.stop(this.task);
                                alert(obj.error);

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'DIRFDialect',
                                        'destroySession'
                                    ),
                                    params: { sid: obj.sid }
                                });

                            }

                            if (obj.pct) this.getProgressBar().updateProgress(obj.pct, obj.pctText, true);
                            else this.getProgressBar().updateProgress(0, 'Aguardando informações', true);
                        },
                        scope: this
                    });
                },

                processSession: function (obj) {
                    this.task = Ext.TaskMgr.start({
                        interval: (5 * 1000),
                        run: this.upgradeProgress,
                        scope: this,
                        args: [obj.sid]
                    });

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            'start'
                        ),
                        params: {
                            sid: obj.sid
                        },
                        scope: this
                    });
                },

                getFormPanel: function () {

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            labelAlign: 'top',
                            items: [
                                new toolkit.gfp.FolhaPagamentoField({
                                    fieldLabel: 'Folha de Pagamento',
                                    names: {
                                        ano: 'folha_ano',
                                        mes: 'folha_mes',
                                        tipo: 'folha_tipo'
                                    },
                                    values: this.params
                                }), {
                                    xtype: 'rest-autocompletefield',
                                    fieldLabel: 'Modelo de Folha',
                                    name: 'folha_modelo',
                                    rest: 'rh.gfp.payroll.ModelPayrollRestful'
                                }
                            ]
                        });

                    return this.formPanel
                },

                getProgressBar: function () {
                    if (!this.progressBar) {
                        this.progressBar = new Ext.ProgressBar({
                            text: 'Processo ainda não foi iniciado.'
                        });
                    }

                    return this.progressBar;
                },

                constructor: function (cf) {
                    if (!cf) cf = {};

                    Ext.apply(
                        cf,
                        {
                            title: 'Gerador de Arquivos de Crédito',
                            closable: true,
                            modal: true,
                            resizable: false,
                            border: false,
                            width: 480,
                            buttons: [
                                {
                                    text: 'Iniciar',
                                    handler: this.start,
                                    scope: this
                                }, {
                                    text: 'Cancelar',
                                    handler: this.destroy,
                                    scope: this
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ModeloFolha.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());

                    // this.add({
                    //     xtype: 'panel',
                    //     frame: true,
                    //     style: 'margin-top:5px',
                    //     items: new Ext.form.FieldSet({
                    //         title: 'Status do processo de geração',
                    //         style: 'margin:5px',
                    //         items: this.getProgressBar()
                    //     })
                    // });
                }
            }
        ),

        CopyContaCredito: Ext.extend(
            toolkit.widget.CommanderController,
            {
                controller: 'GFPCopyCreditoConta',

                getFormPanel: function () {
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            items: [
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "De",
                                    allowBlank: false,
                                    rest: "rh.gfp.payroll.PayrollTypeRestful",
                                    name: "from"
                                },
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Para",
                                    allowBlank: false,
                                    rest: "rh.gfp.payroll.PayrollTypeRestful",
                                    name: "to"
                                },
                                {
                                    xtype: 'datefield',
                                    name: 'vigencia',
                                    fieldLabel: 'Data da vigência'
                                }
                            ]
                        });

                    return this.formPanel;
                },

                constructor: function () {
                    var cf = {
                        title: 'Copiar Contas de Crédito ',
                        closable: true,
                        modal: true,
                        resizable: false,
                        border: false,
                        width: 350,
                        buttons: [
                            {
                                text: 'Copiar',
                                scope: this,
                                handler: this.start
                            },
                            {
                                text: 'Cancelar',
                                handler: this.destroy,
                                scope: this
                            }
                        ]
                    };

                    toolkit.gfp.CopyContaCredito.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());
                }
            }
        ),

        GeradorIgeprev: Ext.extend(
            toolkit.widget.CommanderController,
            {
                controller: 'GFPGeradorIgeprev',

                constructor: function (folha, mes, ano) {
                    var cf = {
                        folha: folha,
                        mes: mes,
                        ano: ano,
                        title: 'Gerador de arquivos do IGEPREV',
                        closable: true,
                        modal: true,
                        resizable: false,
                        border: false,
                        width: 500,
                        buttons: [
                            {
                                text: 'Gerar Arquivo',
                                handler: this.builder,
                                scope: this,
                                handler: this.start
                            },
                            {
                                text: 'Cancelar',
                                handler: this.destroy,
                                scope: this
                            }
                        ]
                    };

                    toolkit.gfp.GeradorIgeprev.superclass.constructor.call(this, cf);
                    this.add(this.getFormPanel());
                },

                getDownloadUrl: function (obj) {
                    return toolkit.util.Normalize.controller_action(
                        this.controller,
                        'getFile'
                    ) + '?sid=' + obj.sid +
                        '&ano=' + this.ano +
                        '&mes=' + this.mes +
                        '&folha=' + this.folha;
                },

                updateInfoProgress: function (obj) {
                    this.getProgressBar().updateProgress(obj.pct, obj.pctText, true);
                    this.getGeneralProgressBar().updateProgress(obj.pctGeral, obj.pctGeralText, true);
                },

                getFormPanel: function () {
                    if (this.formPanel == undefined) {
                        this.formPanel = new Ext.form.FormPanel({
                            border: false,
                            frame: true,
                            buttonAlign: 'center',
                            labelWidth: 120,
                            items: [
                                {
                                    width: 600,
                                    xtype: 'fieldset',
                                    layout: 'table',
                                    title: 'Gerar os Arquivos',
                                    layoutConfig: {
                                        columns: 2
                                    },
                                    defaults: {
                                        labelWidth: 180,
                                        labelAlign: 'left'
                                    },
                                    items: [
                                        {
                                            name: 'folha',
                                            xtype: 'hidden',
                                            value: this.folha
                                        }
                                    ]
                                }, {
                                    xtype: 'fieldset',
                                    title: 'Status da geração do arquivo',
                                    items: [
                                        this.getGeneralProgressBar(),
                                        this.getProgressBar()
                                    ]
                                }
                            ]
                        });
                    }

                    return this.formPanel;
                },

                getGeneralProgressBar: function () {
                    if (!this.generalProgressBar)
                        this.generalProgressBar = new Ext.ProgressBar({})

                    return this.generalProgressBar;
                },

                getProgressBar: function () {
                    if (!this.progressBar)
                        this.progressBar = new Ext.ProgressBar({
                            style: 'margin-top:5px'
                        })

                    return this.progressBar;
                }
            }
        ),

        GeradorArquivoCredito: Ext.extend(
            Ext.Window,
            {
                controller: 'GFPGeradorArquivoCredito',

                start: function () {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(this.controller, 'createSessionId'),
                        params: this.getFormPanel().getForm().getValues(),
                        success: function (request) {
                            var obj = Ext.decode(request.responseText);
                            this.processSession(obj);
                        },
                        failure: function (request) {
                            Ext.Msg.show({
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: 'Ocorreu um erro, tente novamente mais tarde.'
                            })
                        },
                        scope: this
                    })
                },

                getDownloadUrl: function (obj) {
                    return toolkit.util.Normalize.controller_action(
                        this.controller,
                        'getFile'
                    ) + '?sid=' + obj.sid +
                        '&folha_tipo=' + obj.folha_tipo +
                        '&folha_mes=' + obj.folha_mes +
                        '&folha_ano=' + obj.folha_ano +
                        '&banco=' + obj.banco;
                },

                upgradeProgress: function (sid) {
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            'getSessionInformation'
                        ),
                        params: {
                            sid: sid
                        },
                        success: function (request) {
                            var obj = Ext.decode(request.responseText);

                            if (obj.done && !obj.error) {
                                var url = this.getDownloadUrl(obj)

                                var width = 235;
                                var height = 175;
                                var left = (screen.width - width) / 2;
                                var top = (screen.height - height) / 2;

                                window.open(
                                    url,
                                    'buildFile',
                                    'status=no, width=' + width + ', height=' + height + ', toolbar=no, resizable=no, left=' + left + ', top=' + top
                                );

                                Ext.TaskMgr.stop(this.task);

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        this.controller,
                                        'destroySession'
                                    ),
                                    params: { sid: obj.sid }
                                });
                            }
                            else if (obj.error) {

                                Ext.TaskMgr.stop(this.task);
                                alert(obj.error);

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action(
                                        'DIRFDialect',
                                        'destroySession'
                                    ),
                                    params: { sid: obj.sid }
                                });

                            }

                            if (obj.pct) this.getProgressBar().updateProgress(obj.pct, obj.pctText, true);
                            else this.getProgressBar().updateProgress(0, 'Aguardando informações', true);
                        },
                        scope: this
                    });
                },

                processSession: function (obj) {
                    this.task = Ext.TaskMgr.start({
                        interval: (5 * 1000),
                        run: this.upgradeProgress,
                        scope: this,
                        args: [obj.sid]
                    });

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            'start'
                        ),
                        params: {
                            sid: obj.sid
                        },
                        scope: this
                    });
                },

                getFormPanel: function () {

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            labelAlign: 'top',
                            items: [
                                new toolkit.gfp.FolhaPagamentoField({
                                    fieldLabel: 'Folha de Pagamento',
                                    names: {
                                        ano: 'folha_ano',
                                        mes: 'folha_mes',
                                        tipo: 'folha_tipo'
                                    },
                                    values: this.params
                                }),
                                {
                                    width: 395,
                                    xtype: 'combo',
                                    fieldLabel: 'Banco Convêniado',
                                    store: new Ext.data.JsonStore({
                                        url: toolkit.util.Normalize.controller_action('GFPControlador', 'store'),
                                        baseParams: {
                                            model: 'Banco'
                                        },
                                        fields: ['id', 'description'],
                                        root: 'result'
                                    }),
                                    triggerAction: 'all',
                                    valueField: 'id',
                                    displayField: 'description',
                                    editable: false,
                                    hiddenName: 'banco'
                                }
                            ]
                        });

                    return this.formPanel
                },

                getProgressBar: function () {
                    if (!this.progressBar) {
                        this.progressBar = new Ext.ProgressBar({
                            text: 'Processo ainda não foi iniciado.'
                        });
                    }

                    return this.progressBar;
                },

                constructor: function (cf) {
                    if (!cf) cf = {};

                    Ext.apply(
                        cf,
                        {
                            title: 'Gerador de Arquivos de Crédito',
                            closable: true,
                            modal: true,
                            resizable: false,
                            border: false,
                            width: 425,
                            buttons: [
                                {
                                    text: 'Iniciar',
                                    handler: this.start,
                                    scope: this
                                }, {
                                    text: 'Cancelar',
                                    handler: this.destroy,
                                    scope: this
                                }
                            ]
                        }
                    );

                    toolkit.gfp.GeradorArquivoCredito.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());

                    this.add({
                        xtype: 'panel',
                        frame: true,
                        style: 'margin-top:5px',
                        items: new Ext.form.FieldSet({
                            title: 'Status do processo de geração',
                            style: 'margin:5px',
                            items: this.getProgressBar()
                        })
                    });
                }
            }
        ),

        GeradorRAIS: Ext.extend(
            toolkit.widget.CommanderController,
            {
                controller: 'RAISGerador',

                getProgressBar: function () {
                    if (!this.progressBar)
                        this.progressBar = new Ext.ProgressBar({});

                    return this.progressBar;
                },

                getFormPanel: function () {
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            items: [
                                {
                                    xtype: 'fieldset',
                                    items: [
                                        {
                                            name: 'ano_base',
                                            xtype: 'numberfield',
                                            fieldLabel: 'Ano base',
                                            value: (new Date().getFullYear() - 1)
                                        },
                                        {
                                            name: 'retificadora',
                                            xtype: 'checkbox',
                                            fieldLabel: 'Retificadora',
                                            checked: false
                                        }
                                    ]
                                }, {
                                    xtype: 'fieldset',
                                    title: 'Status',
                                    items: this.getProgressBar()
                                }
                            ]
                        });

                    return this.formPanel;
                },

                constructor: function (cf) {
                    if (!cf) cf = {};

                    Ext.apply(
                        cf,
                        {
                            title: 'Relação Anual de Informações Sociais',
                            closable: true,
                            modal: true,
                            resizable: false,
                            border: false,
                            width: 315,
                            buttons: [
                                {
                                    text: 'Iniciar',
                                    handler: this.start,
                                    scope: this
                                }, {
                                    text: 'Cancelar',
                                    handler: this.destroy,
                                    scope: this
                                }
                            ]
                        }
                    );

                    toolkit.gfp.GeradorRAIS.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());
                }
            }
        ),

        GeradorArquivoSEFIP: Ext.extend(
            toolkit.widget.CommanderController,
            {
                controller: 'GFPGeradorArquivoSEFIP',

                getDownloadUrl: function (obj) {
                    return toolkit.util.Normalize.controller_action(
                        this.controller,
                        'getFile'
                    ) + '?sid=' + obj.sid +
                        '&folha_tipo=' + obj.folha_tipo +
                        '&folha_mes=' + obj.folha_mes +
                        '&folha_ano=' + obj.folha_ano;
                },

                getProgressBar: function () {
                    if (!this.progressBar)
                        this.progressBar = new Ext.ProgressBar({})

                    return this.progressBar;
                },

                getFormPanel: function () {

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            labelAlign: 'top',
                            items: [
                                new toolkit.gfp.FolhaPagamentoField({
                                    fieldLabel: 'Folha de Pagamento',
                                    names: {
                                        ano: 'folha_ano',
                                        mes: 'folha_mes',
                                        tipo: 'folha_tipo'
                                    },
                                    values: this.params
                                })
                            ]
                        });

                    return this.formPanel
                },

                constructor: function (cf) {
                    if (!cf) cf = {};

                    Ext.apply(
                        cf,
                        {
                            title: 'Gerador de Arquivos SEFIP',
                            closable: true,
                            modal: true,
                            resizable: false,
                            border: false,
                            width: 425,
                            buttons: [
                                {
                                    text: 'Iniciar',
                                    handler: this.start,
                                    scope: this
                                }, {
                                    text: 'Cancelar',
                                    handler: this.destroy,
                                    scope: this
                                }
                            ]
                        }
                    );

                    toolkit.gfp.GeradorArquivoSEFIP.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());

                    this.add({
                        xtype: 'panel',
                        frame: true,
                        style: 'margin-top:5px',
                        items: new Ext.form.FieldSet({
                            title: 'Status do processo de geração',
                            style: 'margin:5px',
                            items: this.getProgressBar()
                        })
                    });
                }
            }
        ),

        RecalculoFolhaPanel: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function (cfg) {
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: [
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Folha de Pagamento",
                                    allowBlank: false,
                                    rest: "rh.gfp.payroll.PayrollRestful",
                                    name: "payroll",
                                    value: (cfg && cfg.payroll ? cfg.payroll.pk : ''),
                                }, {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Modelo",
                                    allowBlank: true,
                                    rest: "rh.gfp.payroll.ModelPayrollRestful",
                                    name: "model",
                                },
                            ]
                        });

                    return this.formPanel;
                },

                process: function () {
                    var params = this.getFormPanel().getForm().getValues()
                    params['possession_group'] = this.possession_group;

                    Ext.Msg.show({
                        msg: 'Tem certeza que deseja processar o recalculo para folha selecionada?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function (b) {
                            if (b == 'no') return;

                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action('GFPPayroll', 'recalculate'),
                                params: params
                            });

                            this.destroy();
                        }
                    })
                },

                constructor: function (cf) {

                    if (cf == null) cf = {};

                    this.possession_group = cf.possession_group;

                    Ext.apply(
                        cf,
                        {
                            title: 'Recalculo da Folha de Pagamento',
                            closable: true,
                            border: false,
                            resizable: false,
                            modal: true,
                            width: 550,
                            buttons: [
                                {
                                    text: 'Recalcular',
                                    scope: this,
                                    handler: this.process
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ],
                            items: [
                                this.getFormPanel(cf)
                            ]
                        }
                    );

                    toolkit.gfp.RecalculoFolhaPanel.superclass.constructor.call(this, cf);

                    // this.add(this.getFormPanel());
                }
            }
        ),

        CopyPanel: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function (cfg) {
                    console.debug(cfg);
                    console.debug(this);
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: [
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Folha Base",
                                    allowBlank: false,
                                    rest: "rh.gfp.payroll.PayrollRestful",
                                    name: "payroll",
                                    value: (cfg && cfg.payroll ? cfg.payroll.pk : ''),
                                },
                                new toolkit.gfp.FolhaPagamentoField({
                                    fieldLabel: 'Destino',
                                    names: {
                                        ano: 'year',
                                        mes: 'month',
                                        tipo: 'type_payroll'
                                    }
                                }), {
                                    xtype: 'fieldset',
                                    title: 'Se a folha de destino ja existe',
                                    items: [
                                        {
                                            xtype: 'radio',
                                            inputValue: 'CHANGED',
                                            boxLabel: 'Manter alterações já existentes na folha!',
                                            name: 'type_of_copy'
                                        },
                                        {
                                            xtype: 'radio',
                                            inputValue: 'NEW',
                                            boxLabel: 'Apagar os eventos copiados e manter os novos eventos já criados na folha!',
                                            name: 'type_of_copy'
                                        },
                                        {
                                            xtype: 'radio',
                                            inputValue: 'DELETE',
                                            boxLabel: 'Apagar todos eventos antes de copiar',
                                            checked: true,
                                            name: 'type_of_copy'
                                        }
                                    ]
                                }, {
                                    xtype: 'fieldset',
                                    // title: '',
                                    items: [
                                        {
                                            xtype: 'checkbox',
                                            checked: true,
                                            boxLabel: 'Gerar bases de remuneração',
                                            name: 'generate_bases'
                                        }
                                    ]
                                }
                            ]
                        });

                    return this.formPanel;
                },

                start: function () {
                    Ext.Msg.show({
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OKCANCEL,
                        msg: 'A copia da folha será realizada no servidor, como este processo pode demorar<br/>' +
                            'um pouco, o sistema ira notificar quando o processo tiver terminado.',
                        scope: this,
                        fn: function (b) {
                            if (b == 'cancel') return;

                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action('GFPPayroll', 'copy_payroll'),
                                params: this.getFormPanel().getForm().getValues()
                            });

                            this.destroy();
                        }
                    });
                },

                constructor: function (cf) {
                    Ext.apply(
                        cf,
                        {
                            title: 'Copia de Folha de Pagamento',
                            closable: true,
                            resizable: false,
                            width: 650,
                            border: false,
                            modal: true,
                            buttons: [
                                {
                                    text: 'Copiar',
                                    scope: this,
                                    handler: this.start
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ],
                            items: [
                                this.getFormPanel(cf),
                            ]
                        }
                    );

                    toolkit.gfp.CopyPanel.superclass.constructor.call(this, cf);
                }
            }
        ),

        ResumoGeralEvento: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function () {
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: [
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Evento",
                                    allowBlank: true,
                                    rest: "rh.gfp.payroll.EventRestful",
                                    name: "evento",
                                },
                                {
                                    xtype: 'combobox',
                                    hiddenName: 'employee_type',
                                    fieldLabel: 'Tipo',
                                    store: [
                                        ['M', 'MEMBRO'],
                                        ['S', 'SERVIDOR'],
                                        ['E', 'ESTAGIÁRIO']
                                    ],
                                    allowBlank: true,
                                    triggerAction: 'all',
                                    // value: 'M'
                                }
                            ]
                        });

                    return this.formPanel;
                },

                build: function (type) {
                    var event = this.getFormPanel().getForm().getValues().evento
                    var employee_type = this.getFormPanel().getForm().getValues().employee_type
                    var payroll = this.params.folha
                    var description = this.params.description = !undefined ? this.params.description : ''
                    engine.mq.Report.request({
                        report: '/to/mpe/gfp/employee_by_event',
                        waitMessage: 'Gerando relatório...',
                        params: {

                            outfile: 'resumo-de-evento-por-evento-folha-' + description + '-evento-' + event,
                            report_name: 'Resumo de Evento - por Evento',
                            folha: payroll,
                            evento: event,
                            employee_type: employee_type
                        }

                    }, type);

                    this.destroy();
                },

                constructor: function (cf) {
                    if (!cf) cf = {}

                    Ext.apply(
                        cf,
                        {
                            title: 'Resumo Geral de Eventos',
                            closable: true,
                            resizable: false,
                            width: 330,
                            border: false,
                            modal: true,
                            buttons: [
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
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo ODT',
                                                type: 'ODT',
                                                iconCls: 'icon-ged icon-ged-application-msword',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo XLS',
                                                type: 'XLS',
                                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                        ]
                                    },
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ResumoGeralEvento.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());
                }
            }
        ),

        ServidoresPorConsignacaoTipo: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function () {
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: [
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Folha",
                                    allowBlank: true,
                                    rest: "rh.gfp.payroll.PayrollRestful",
                                    name: "folha",
                                    disabled: true,
                                    value: this.params.folha,
                                },
                                {
                                    xtype: "rest-autocompletefield",
                                    fieldLabel: "Evento de consignação",
                                    allowBlank: false,
                                    rest: "rh.gfp.payroll.EventRestful",
                                    name: "evento",
                                },
                                {
                                    xtype: 'combo',
                                    hiddenName: 'employee_type',
                                    fieldLabel: 'Tipo',
                                    store: [
                                        ['0', 'TODOS'],
                                        ['M', 'MEMBRO'],
                                        ['S', 'SERVIDOR']
                                    ],
                                    triggerAction: 'all',
                                    value: '0',
                                }
                            ]
                        });

                    return this.formPanel;
                },

                build: function (type) {
                    var event = this.getFormPanel().getForm().getValues().evento
                    var employee_type = this.getFormPanel().getForm().findField('employee_type')
                    var payroll = this.params.folha
                    engine.mq.Report.request({
                        report: '/to/mpe/gfp/type_employee_by_event',
                        waitMessage: 'Gerando relatório...',
                        params: {

                            outfile: 'consignacao-por-tiposervidor-' + employee_type.getRawValue() + '-evento-' + event,
                            report_name: 'Servidores por consignação e tipo',
                            folha: payroll,
                            evento: event,
                            employee_type: employee_type.value
                        }

                    }, type);

                    this.destroy();
                },

                constructor: function (cf) {
                    if (!cf) cf = {}

                    Ext.apply(
                        cf,
                        {
                            title: 'Consignação por tipo de servidor',
                            closable: true,
                            resizable: false,
                            width: 330,
                            border: false,
                            modal: true,
                            buttons: [
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    // style: 'margin-top: 10px',
                                    text: 'Gerar Relatório',
                                    width: 100,
                                    height: 25,
                                    scope: this,
                                    handler: function () {
                                        this.build('PDF');
                                    },
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ServidoresPorConsignacaoTipo.superclass.constructor.call(this, cf);

                    this.add(this.getFormPanel());
                }
            }
        ),

        ResumoGeralEventoConsignatario: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function () {
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: [
                                {
                                    xtype: 'combo',
                                    fieldLabel: 'Consignatario',
                                    hiddenField: 'plano',
                                    hiddenName: 'plano',
                                    store: new Ext.data.JsonStore({
                                        proxy: new Ext.data.HttpProxy({
                                            url: toolkit.util.Normalize.controller_action('PCConsignatario', 'list'),
                                            disableCaching: true,
                                            method: 'GET'
                                        }),
                                        baseParams: this.params,
                                        root: 'root',
                                        fields: ['pk', 'description']
                                    }),
                                    displayField: 'description',
                                    valueField: 'pk',
                                    emptyText: 'Selecione o Consignatário',
                                    width: 295,
                                    triggerAction: 'all'

                                },
                                {
                                    xtype: 'combobox',
                                    hiddenName: 'employee_type',
                                    fieldLabel: 'Tipo',
                                    store: [
                                        ['M', 'MEMBRO'],
                                        ['S', 'SERVIDOR'],
                                        ['E', 'ESTAGIÁRIO']
                                    ],
                                    allowBlank: true,
                                    triggerAction: 'all',
                                }
                            ]
                        });

                    return this.formPanel;
                },

                build: function (type) {
                    console.debug('');
                    var payroll = this.params.folha
                    var description = this.params.description = !undefined ? this.params.description : ''
                    var plan = this.getFormPanel().getForm().getValues().plano
                    var employee_type = this.getFormPanel().getForm().getValues().employee_type
                    engine.mq.Report.request({
                        report: '/to/mpe/gfp/employee_by_consignee',
                        waitMessage: 'Gerando relatório...',
                        params: {

                            outfile: 'resumo-de-evento-por-consignatario-folha-' + description,
                            report_name: 'Resumo de Evento - por Consignatário',
                            folha: payroll,
                            plano: plan,
                            employee_type: employee_type
                        }

                    }, type);

                    this.destroy();
                },

                constructor: function (cf) {
                    if (!cf) cf = {}

                    Ext.apply(
                        cf,
                        {
                            title: 'Resumo Geral de Eventos por consignatário',
                            closable: true,
                            resizable: false,
                            width: 330,
                            border: false,
                            modal: true,
                            buttons: [
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
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo ODT',
                                                type: 'ODT',
                                                iconCls: 'icon-ged icon-ged-application-msword',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo XLS',
                                                type: 'XLS',
                                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                        ]
                                    },
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ResumoGeralEventoConsignatario.superclass.constructor.call(this, cf);
                    this.add(this.getFormPanel());
                }
            }
        ),
        
        ConferenciaFolha: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function() {
                    var items = [
                        {
                            fieldLabel: 'Tipo de Servidor',
                            hiddenName: 'type_by_possession',
                            xtype: 'combo',
                            store: [
                                [99, 'Geral'],
                                [0, 'Membros Ativos'],
                                [1, 'Servidores Ativos'],
                                [2, 'Comissionados'],
                                [3, 'Membros Inativos'],
                                [4, 'Servidores Inativos'],
                                [5, 'Pensionistas'],
                                [6, 'Adidos'],
                                [7, 'Estagiários/Residentes'],
                            ],
                            triggerAction: 'all',
                            width: 250
                        },
                        {
                            xtype: "checkbox",
                            boxLabel: "Unificar",
                            fieldLabel: "Unificar",
                            allowBlank: true,
                            hideLabel: true,
                            name: "unify",
                            checked: true,
                        }
                    ];

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: items,
                        });

                    return this.formPanel;
                },


                build: function (type) {
                    var conjunto_geral = "'MBR','MBR2','MEL','MCM','MEC','MEL2','MCM2','MEC2','RFC','REQ','EXT','RCM','EFE','ECM','EFC','CMS','MAP','SAP','MAP2','APO','BFP'"
                    var conjunto_servidores = [
                        "'MBR','MBR2','MEL','MCM','MEC','MEL2','MCM2','MEC2'",
                        "'EFE','ECM','EFC'",
                        "'CMS',",
                        "'MAP','MAP2'",
                        "'SAP','MAP2'",
                        "'BFP',",
                        "'RFC','REQ','EXT','RCM'",
                        "'EST','RES'",
                    ]

                    var tipo_de_servidor = this.getFormPanel().getForm().getValues().type_by_possession
                    var unify = this.getFormPanel().getForm().getValues().unify

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'PaycheckConferenceReport',
                            'generate_paycheck_conference'
                        ),
                        params: {
                            payroll: this.params.folha,
                            previous_payroll: this.params.folha_anterior,
                            type_by_possession: tipo_de_servidor == '' || tipo_de_servidor == 99 ? conjunto_geral : conjunto_servidores[tipo_de_servidor],
                            unify:unify,
                            output_format: type
                        },
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            if (obj.success){
                                Ext.Msg.show({
                                    title: 'Solicitando Relatório',
                                    msg: obj.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                                if (obj.download){
                                    var RemoteObserver = core.RemoteObserver;
                                    var cb = RemoteObserver.on('base-report', {
                                        scope: this,
                                        fn: function (data) {
                                            setTimeout(
                                                function() {
                                                    toolkit.util.downloadFile({
                                                        url: data.path,
                                                        filename: data.filename,
                                                        approach: 'download',
                                                    });
                                                    RemoteObserver.un('base-report', {scope: this})
                                                
                                                },
                                                1000
                                            );
                                        
                                        }
                                    });
            
                                    setTimeout( function() {
                                        Ext.Ajax.request({
                                            url: toolkit.util.Normalize.controller_action(
                                                this.CLASS_NAME,
                                                'marker'
                                            ),
                                            params: {
                                                uuid: obj.uuid
                                            },
                                            success: function() {},
                                            failure: function() {},
                                        });
                                    },
                                    2000);
            
            
                                }
                            }else{
                                Ext.Msg.show({
                                    title: 'Error',
                                    msg: obj.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function() {
                            Ext.Msg.show({
                                title: this.title,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                            });
                        },
                        scope: this
                    });



                    this.destroy();
                },

                constructor: function (cf) {
                    if (!cf) cf = {}

                    Ext.apply(
                        cf,
                        {
                            title: 'Conferência da Folha',
                            closable: true,
                            resizable: false,
                            width: 280,
                            border: false,
                            modal: true,
                            buttons: [
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    // style: 'margin-top: 10px',
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
                                                    this.build(item.type);
                                                }
                                            },
                                            // {
                                            //     text: 'Arquivo ODT',
                                            //     type: 'ODT',
                                            //     iconCls: 'icon-ged icon-ged-application-msword',
                                            //     scope: this,
                                            //     handler: function (item) {
                                            //         this.build(item.type);
                                            //     }
                                            // },
                                            {
                                                text: 'Arquivo XLS',
                                                type: 'XLS',
                                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                        ]
                                    },
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ConferenciaFolha.superclass.constructor.call(this, cf);
                    this.add(this.getFormPanel());
                }
            }
        ),
        
        ClassificacaoGeral: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function() {
                    var items = [
                        {
                            fieldLabel: 'Tipo de Servidor',
                            hiddenName: 'type_by_possession',
                            xtype: 'combo',
                            store: [
                                [99, 'Geral'],
                                [0, 'Membros Ativos'],
                                [1, 'Servidores Ativos'],
                                [2, 'Membros Inativos'],
                                [3, 'Servidores Inativos'],
                                [4, 'Pensionistas'],
                                [5, 'Adidos'],
                                [6, 'Estagiários/Residentes'],
                            ],
                            triggerAction: 'all',
                            width: 250
                        },
                    ]

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: items,
                        });

                    return this.formPanel;
                },


                build: function (type) {
                    var conjunto_geral = "'MBR','MBR2','MEL','MCM','MEC','MEL2','MCM2','MEC2','EFE','ECM','EFC','CMS','RFC','REQ','EXT','RCM','MAP','SAP','MAP2','APO','BFP'"
                    var conjunto_servidores = [
                        "'MBR','MBR2','MEL','MCM','MEC','MEL2','MCM2','MEC2'",
                        "'EFE','ECM','EFC','CMS','RCM'",
                        "'MAP','MAP2'",
                        "'SAP','APO'",
                        "'BFP'",
                        "'RFC','REQ','EXT'",
                        "'EST','RES'",
                    ]
                    
                    var payroll = this.params.folha
                    var tipo_de_servidor = this.getFormPanel().getForm().getValues().type_by_possession
                    var type_by_possession = tipo_de_servidor == '' || tipo_de_servidor == 99 ? conjunto_geral : conjunto_servidores[tipo_de_servidor]

                    engine.mq.Report.request({
                        report: '/to/mpe/gfp/general_classification_analytical',
                        waitMessage: 'Gerando relatório...',
                        params: {

                            outfile: 'analitico-' + this.params.description,
                            report_name: 'Classificacao Geral de Folha - Analítico',
                            folha: payroll,
                            type_by_possession: type_by_possession
                        }

                    }, type);

                    this.destroy();
                },

                constructor: function (cf) {
                    if (!cf) cf = {}

                    Ext.apply(
                        cf,
                        {
                            title: 'Classificacao Geral de Folha - Analítico',
                            closable: true,
                            resizable: false,
                            width: 280,
                            border: false,
                            modal: true,
                            buttons: [
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    // style: 'margin-top: 10px',
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
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo ODT',
                                                type: 'ODT',
                                                iconCls: 'icon-ged icon-ged-application-msword',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo XLS',
                                                type: 'XLS',
                                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                        ]
                                    },
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ClassificacaoGeral.superclass.constructor.call(this, cf);
                    this.add(this.getFormPanel());
                }
            }
        ),

        ClassificacaoGeralSintetico: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function() {
                    var items = [
                        {
                            fieldLabel: 'Tipo de Servidor',
                            hiddenName: 'type_by_possession',
                            xtype: 'combo',
                            store: [
                                [0, 'Ativos'],
                                [1, 'Inativos'],
                                [2, 'Pensionistas'],
                                [3, 'Adidos'],
                                [4, 'Comissionados'],
                                [5, 'Servidores Efetivos'],
                                [6, 'Membros Efetivos'],
                                [7, 'Estagiários/Residentes'],
                            ],
                            triggerAction: 'all',
                            width: 250
                        },
                    ]

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: items,
                        });

                    return this.formPanel;
                },


                build: function (type) {
                    var conjunto_geral = "'MBR','MBR2','MEL','MCM','MEC','MEL2','MCM2','MEC2','EFE','ECM','EFC','CMS','RFC','REQ','EXT','RCM','MAP','SAP','MAP2','APO','BFP'"
                    var conjunto_servidores = [
                        "'MBR','MBR2','MEL','MCM','MEC','MEL2','MCM2','MEC2','CMS','EFE','ECM','EFC','RCM'",
                        "'MAP','SAP','MAP2','APO'",
                        "'BFP'",
                        "'RFC','REQ','EXT'",
                        "'CMS','RCM'",
                        "'EFE','ECM','EFC'",
                        "'MBR','MBR2','MEL','MCM','MEC','MEL2','MCM2','MEC2'",
                        "'EST','RES'",
                    ]
                    
                    var payroll = this.params.folha
                    var tipo_de_servidor = this.getFormPanel().getForm().getValues().type_by_possession
                    var type_by_possession = tipo_de_servidor == '' || tipo_de_servidor == 99 ? conjunto_geral : conjunto_servidores[tipo_de_servidor]

                    engine.mq.Report.request({
                        report: '/to/mpe/gfp/general_classification_synthetic',
                        waitMessage: 'Gerando relatório...',
                        params: {

                            outfile: 'sintetico-' + this.params.description,
                            report_name: 'Classificacao Geral de Folha - Sintético',
                            folha: payroll,
                            type_by_possession: type_by_possession
                        }

                    }, type);

                    this.destroy();
                },

                constructor: function (cf) {
                    if (!cf) cf = {}

                    Ext.apply(
                        cf,
                        {
                            title: 'Classificacao Geral de Folha - Sintético',
                            closable: true,
                            resizable: false,
                            width: 280,
                            border: false,
                            modal: true,
                            buttons: [
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    // style: 'margin-top: 10px',
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
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo ODT',
                                                type: 'ODT',
                                                iconCls: 'icon-ged icon-ged-application-msword',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo XLS',
                                                type: 'XLS',
                                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                        ]
                                    },
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ClassificacaoGeralSintetico.superclass.constructor.call(this, cf);
                    this.add(this.getFormPanel());
                }
            }
        ),

        AnaliticoFolha: Ext.extend(
            Ext.Window,
            {
                getTypeByPossessionChoiceField: function () {
                    var types_by_possession_filtered = this.params.types_by_possession_filtered
                    if (!this.typeByPossessionChoiceField) {
                        this.typeByPossessionChoiceField = Ext._create('standard.fields.ChoiceField', {
                            width: 450,
                            hiddenName: 'type_by_possession',
                            fieldLabel: 'Tipo de Servidor',
                            choiceId: 'rh.CLASSIF_EMPLOYEE_BY_POSSESSION',
                            valueField: 'cvalue',
                        });
                        var store = this.typeByPossessionChoiceField.getStore();
                        var filter = Ext.decode(store.baseParams.filter);
                        filter.push({ property: 'value__in', value: types_by_possession_filtered, stage: 1 });
                        store.baseParams.filter = Ext.encode(filter);
                        store.load();
                    }
                    return this.typeByPossessionChoiceField;
                },

                getFormPanel: function () {
                    var items = [];

                    items.push(this.getTypeByPossessionChoiceField());

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: items,
                        });

                    return this.formPanel;
                },


                build: function (type) {
                    console.debug('');
                    var payroll = this.params.folha
                    var type_by_possession = this.getFormPanel().getForm().getValues().type_by_possession
                    engine.mq.Report.request({
                        report: '/to/mpe/gfp/paycheck_analytical',
                        waitMessage: 'Gerando relatório...',
                        params: {

                            outfile: 'analitico-' + this.params.description,
                            report_name: 'Analitico da Folha de Pagamento',
                            folha: payroll,
                            type_by_possession: type_by_possession
                        }

                    }, type);

                    this.destroy();
                },

                constructor: function (cf) {
                    if (!cf) cf = {}

                    Ext.apply(
                        cf,
                        {
                            title: 'Analitico da Folha',
                            closable: true,
                            resizable: false,
                            width: 480,
                            border: false,
                            modal: true,
                            buttons: [
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    // style: 'margin-top: 10px',
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
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo ODT',
                                                type: 'ODT',
                                                iconCls: 'icon-ged icon-ged-application-msword',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo XLS',
                                                type: 'XLS',
                                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                        ]
                                    },
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.AnaliticoFolha.superclass.constructor.call(this, cf);
                    this.add(this.getFormPanel());
                }
            }
        ),

        ArquivoBancarioConsig: Ext.extend(
            Ext.Window,
            {
                controller: 'GFPGenerateCreditFile',

                getFormPanel: function (cfg) {
                    var items = [];

                    items.push({
                        xtype: 'rest-combofield',
                        rest: 'rh.gfp.payroll.PeriodosFolhaRestful',
                        fieldLabel: 'Período',
                        triggerAction: 'all',
                        lazyRender: true,
                        lazyInit: true,
                        displayField: 'unicode',
                        width: 210,
                        name: 'periodo',
                    });
                    items.push({
                        allowBlank: true,
                        fieldLabel: 'Data de pagamento',
                        name: 'dt_pg',
                        xtype: 'datefield',
                        width: 210,
                        value: (cfg && cfg.params && cfg.params.data_pagamento ? cfg.params.data_pagamento : ''),
                        allowBlank: false
                    });

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            items: items,
                        });

                    return this.formPanel;
                },

                build: function () {
                    var params = this.getFormPanel().getForm().getValues()
                    var periodo = params.periodo
                    var dt_pg = params.dt_pg


                    console.log('>>> periodo: '+ periodo)
                    console.log('>>> dt_pg: '+ dt_pg)

                    if(periodo == '' || dt_pg == ''){
                        Ext.Msg.show({
                            title: 'Error',
                            msg: 'Os campos período e Data de pagamento são obrigatórios',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }else{
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                'GFPGerarArquivoConsignado',
                                'gerar_arquivo_bancario_consignado'
                            ),
                            params: {
                                periodo: periodo,
                                dt_pg: dt_pg,
                            },
                            success: function(request) {
                                var obj = Ext.decode(request.responseText);
                                if (obj.success){
                                    Ext.Msg.show({
                                        title: 'Solicitando Relatório',
                                        msg: obj.message,
                                        icon: Ext.Msg.INFO,
                                        buttons: Ext.Msg.OK
                                    });
                                    if (obj.download){
                                        var RemoteObserver = core.RemoteObserver;
                                        var cb = RemoteObserver.on('base-report', {
                                            scope: this,
                                            fn: function (data) {
                                                setTimeout(
                                                    function() {
                                                        toolkit.util.downloadFile({
                                                            url: data.path,
                                                            filename: data.filename,
                                                            approach: 'download',
                                                        });
                                                        RemoteObserver.un('base-report', {scope: this})
                                                    
                                                    },
                                                    1000
                                                );
                                            
                                            }
                                        });            
                                        setTimeout( function() {
                                            Ext.Ajax.request({
                                                url: toolkit.util.Normalize.controller_action(
                                                    this.CLASS_NAME,
                                                    'marker'
                                                ),
                                                params: {
                                                    uuid: obj.uuid
                                                },
                                                success: function() {},
                                                failure: function() {},
                                            });
                                        },
                                        2000);            
                                    }
                                }else{
                                    Ext.Msg.show({
                                        title: 'Error',
                                        msg: obj.message,
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK
                                    });
                                }
                            },
                            failure: function() {
                                Ext.Msg.show({
                                    title: this.title,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                                });
                            },
                            scope: this
                        });
                    }

                    this.destroy();
                },

                constructor: function (cfg) {
                    if (!cfg) cfg = {}

                    Ext.apply(
                        cfg,
                        {
                            title: 'Gerador de arquivo bancário de consignados',
                            closable: true,
                            resizable: false,
                            width: 650,
                            border: false,
                            modal: true,
                            buttons: [
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    text: 'Executar',
                                    width: 85,
                                    height: 25,
                                    scope: this,
                                    handler: function () {
                                        this.build();
                                    }
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ArquivoBancario.superclass.constructor.call(this, cfg);
                    this.add(this.getFormPanel(cfg));
                }
            }
        ),

        ArquivoBancario: Ext.extend(
            Ext.Window,
            {
                controller: 'GFPGenerateCreditFile',

                getTypeByPossessionChoiceField: function () {
                    var types_by_possession_filtered = this.params.types_by_possession_filtered
                    if (!this.typeByPossessionChoiceField) {
                        this.typeByPossessionChoiceField = Ext._create('standard.fields.ChoiceField', {
                            width: 450,
                            hiddenName: 'type_by_possession',
                            fieldLabel: 'Tipo de Servidor',
                            choiceId: 'rh.CLASSIF_EMPLOYEE_BY_POSSESSION',
                            valueField: 'cvalue',
                        });
                        var store = this.typeByPossessionChoiceField.getStore();
                        var filter = Ext.decode(store.baseParams.filter);
                        filter.push({ property: 'value__in', value: types_by_possession_filtered, stage: 1 });
                        store.baseParams.filter = Ext.encode(filter);
                        store.load();
                    }
                    return this.typeByPossessionChoiceField;
                },

                getEmployeersField: function () {
                    if (!this._employeefield)
                        this._employeefield = Ext._create('toolkit.plugins.MultiSelectField', {
                            fieldLabel: 'Servidor(es)',
                            name: 'servidores',
                            hiddenName: 'Servidores',
                            controller: 'RHServidor',
                            conf: {
                                canAdd: false,
                                canEdit: false
                            },
                            displayField: 'description',
                            valueField: 'pk',
                            width: 550,
                        });    
                    return this._employeefield;
                },

                getFormPanel: function (cfg) {
                    var items = [];

                    items.push({
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Folha',
                        name: 'payroll',
                        rest: 'rh.gfp.payroll.PayrollRestful',
                        value: (cfg && cfg.params && cfg.params.payroll ? cfg.params.payroll : ''),
                        allowBlank: false,
                    });
                    items.push({
                        xtype: 'rest-combofield',
                        rest: 'rh.gfp.payroll.ActiveBankingConvenantRestful',
                        fieldLabel: 'Convênio',
                        hiddenName: 'convenant',
                        triggerAction: 'all',
                        lazyRender: true,
                        lazyInit: true,
                        displayField: 'unicode',
                        width: 210,
                    });
                    items.push({
                        fieldLabel: 'Somente pensionistas',
                        xtype: 'checkbox',
                        name: 'somente_pensionistas',
                        allowBlank: true,
                        checked: false,
                    });
                    items.push({
                        allowBlank: true,
                        fieldLabel: 'Data de pagamento',
                        name: 'dt_pg',
                        xtype: 'datefield',
                        width: 210,
                        value: (cfg && cfg.params && cfg.params.data_pagamento ? cfg.params.data_pagamento : ''),
                        allowBlank: false
                    });
                    items.push(this.getEmployeersField());

                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            frame: true,
                            items: items,
                        });

                    return this.formPanel;
                },

                build: function () {
                    var params = this.getFormPanel().getForm().getValues()

                    var payroll = params.payroll
                    var convenant = params.convenant
                    var data_pagamento = params.dt_pg
                    var somente_pensionistas = params.somente_pensionistas

                    var multibox_items = this.getEmployeersField().store.data.items;
                    var _selecteds_employers = []

                    Ext.each(multibox_items, function (item) {
                        _selecteds_employers.push(item.id);
                    });
                    
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'GFPGenerateCreditFile',
                            'generate_file'
                        ),
                        params: {
                            payroll: payroll,
                            convenant: convenant,
                            dt_pg: data_pagamento,
                            employees: _selecteds_employers,
                            somente_pensionistas: somente_pensionistas,
                        },
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            if (obj.success){
                                Ext.Msg.show({
                                    title: 'Solicitando Relatório',
                                    msg: obj.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                                if (obj.download){
                                    var RemoteObserver = core.RemoteObserver;
                                    var cb = RemoteObserver.on('base-report', {
                                        scope: this,
                                        fn: function (data) {
                                            setTimeout(
                                                function() {
                                                    toolkit.util.downloadFile({
                                                        url: data.path,
                                                        filename: data.filename,
                                                        approach: 'download',
                                                    });
                                                    RemoteObserver.un('base-report', {scope: this})
                                                
                                                },
                                                1000
                                            );
                                        
                                        }
                                    });            
                                    setTimeout( function() {
                                        Ext.Ajax.request({
                                            url: toolkit.util.Normalize.controller_action(
                                                this.CLASS_NAME,
                                                'marker'
                                            ),
                                            params: {
                                                uuid: obj.uuid
                                            },
                                            success: function() {},
                                            failure: function() {},
                                        });
                                    },
                                    2000);            
                                }
                            }else{
                                Ext.Msg.show({
                                    title: 'Error',
                                    msg: obj.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        failure: function() {
                            Ext.Msg.show({
                                title: this.title,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                            });
                        },
                        scope: this
                    });

                    this.destroy();
                },

                constructor: function (cfg) {
                    if (!cfg) cfg = {}

                    Ext.apply(
                        cfg,
                        {
                            title: 'Gerador de arquivo bancário',
                            closable: true,
                            resizable: false,
                            width: 650,
                            border: false,
                            modal: true,
                            buttons: [
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    text: 'Executar',
                                    width: 85,
                                    height: 25,
                                    scope: this,
                                    handler: function () {
                                        this.build();
                                    }
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.ArquivoBancario.superclass.constructor.call(this, cfg);
                    this.add(this.getFormPanel(cfg));
                }
            }
        ),

        RelacaoBancaria: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function () {
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            labelAlign: 'top',
                            frame: true,
                            items: [
                                {
                                    xtype: 'combobox',
                                    hiddenName: 'employee_type',
                                    fieldLabel: 'Tipo',
                                    store: [
                                        ['M', 'MEMBRO'],
                                        ['S', 'SERVIDOR'],
                                        ['E', 'ESTAGIÁRIO']
                                    ],
                                    allowBlank: true,
                                    triggerAction: 'all',
                                },
                            ]
                        });

                    return this.formPanel;
                },

                build: function (type) {
                    console.debug(type);
                    var payroll = this.params.folha
                    var employee_type = this.getFormPanel().getForm().getValues().employee_type
                    engine.mq.Report.request({
                        report: '/to/mpe/gfp/bank_relationship_simplified',
                        waitMessage: 'Gerando relatório...',
                        params: {

                            outfile: 'relacaobancariasimples-' + this.params.description,
                            report_name: 'Relação Bancária Simples',
                            folha: payroll,
                            employee_type: employee_type
                        }
                    },
                        type);

                    this.destroy();
                },

                constructor: function (cf) {
                    if (!cf) cf = {}

                    Ext.apply(
                        cf,
                        {
                            title: 'Relação bancária simplificada',
                            closable: true,
                            resizable: false,
                            width: 330,
                            border: false,
                            modal: true,
                            buttons: [
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
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo ODT',
                                                type: 'ODT',
                                                iconCls: 'icon-ged icon-ged-application-msword',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                            {
                                                text: 'Arquivo XLS',
                                                type: 'XLS',
                                                iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                scope: this,
                                                handler: function (item) {
                                                    this.build(item.type);
                                                }
                                            },
                                        ]
                                    },
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.RelacaoBancaria.superclass.constructor.call(this, cf);
                    this.add(this.getFormPanel());
                }
            }
        ),
        LoaderFileGFP: Ext.extend(
            Ext.Window,
            {
                getFormPanel: function (cfg) {
                    if (!this.formPanel)
                        this.formPanel = new Ext.form.FormPanel({
                            // frame: true,
                            labelWidth: 120,
                            items: [
                                {
                                    xtype: 'rest-autocompletefield',
                                    fieldLabel: 'Folha',
                                    name: 'payroll',
                                    rest: 'rh.gfp.payroll.PayrollRestful',
                                    value: (cfg && cfg.payroll ? cfg.payroll.pk : ''),
                                    allowBlank: false,
                                }, {
                                    xtype: 'rest-autocompletefield',
                                    fieldLabel: 'Carregador',
                                    name: 'loader',
                                    rest: 'rh.gfp.classcode.LoaderRestful',
                                    allowBlank: false,
                                }, {
                                    fieldLabel: 'Arquivo',
                                    xtype: 'ged-fileuploadfield',
                                    name: 'file',
                                    allowBlank: false,
                                    width: 365
                                }, {
                                    xtype: 'rest-autocompletefield',
                                    fieldLabel: 'Evento',
                                    name: 'event',
                                    rest: 'rh.gfp.payroll.EventRestful',
                                }, {
                                    xtype: 'checkbox',
                                    fieldLabel: 'Criar Contracheques',
                                    name: 'create',
                                },
                            ],
                        });

                    return this.formPanel;
                },
                execute: function () {
                    var form = this.getFormPanel().getForm();

                    form.waitMsgTarget = this.getFormPanel().getEl();
                    form.submit({
                        url: toolkit.util.Normalize.controller_action('GFPControlador', 'load_file'),
                        
                        success: function(xhr, action) {
                            var rst = action.result;
                            if(rst.success) {
                                this.destroy();
                                Ext.Msg.show({
                                    title: 'Carregando Arquivo',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            }
                            else
                                Ext.Msg.show({
                                    title: 'Carregando Arquivo',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                        },
                        failure: function (form, action) {
                            Ext.Msg.show({
                                title: 'Erro',
                                msg: action.result.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        scope: this,
                        waitMsg: 'Aguarde ...'
                    });
                },

                constructor: function (cfg) {
                    if (!cfg) cfg = {}

                    Ext.apply(
                        cfg,
                        {
                            title: 'Carregar arquivos do FOPAG',
                            closable: true,
                            resizable: false,
                            width: 500,
                            border: false,
                            modal: true,
                            items: [
                                this.getFormPanel(cfg),
                            ],
                            buttons: [
                                {
                                    text: 'Carregar',
                                    scope: this,
                                    handler: this.execute
                                }, {
                                    text: 'Cancelar',
                                    scope: this,
                                    handler: this.destroy
                                }
                            ]
                        }
                    );

                    toolkit.gfp.LoaderFileGFP.superclass.constructor.call(this, cfg);
                }
            }
        ),

        Controlador: Ext.extend(
            Ext.Panel,
            {
                create: function () {
                    var s = this.getGridFolha().getStore();

                    new rh.gfp.payroll.PayrollWindow({
                        title: 'Criar Folha de Pagamento',
                        action: 'create',
                        callback: {
                            success: {
                                scope: this,
                                fn: function () {
                                    s.reload();
                                }
                            }
                        },
                        status_callback: this.status_callback,
                    }).show();
                },

                edit: function () {
                    var s = this.getGridFolha().getStore();
                    // var selection = this.getGridFolha().getSelectionModel().getSelected();
                    var selected = this.getGridFolha().getSelectionModel().getSelected();
                    new rh.gfp.payroll.PayrollWindow({
                        title: 'Editar Folha de Pagamento',
                        action: 'update',
                        values: 'remote',
                        oId: selected.get('pk'),
                        callback: {
                            scope: this,
                            fn: function () {
                                s.reload();
                            }
                        }
                    }).show();
                },

                editPeriodo: function () {
                    var s = this.getGridFolha().getStore();
                    var selected = this.getGridFolha().getSelectionModel().getSelected();

                    if (selected) {
                        new rh.gfp.payroll.PeriodWindow({
                            action: 'update',
                            values: 'remote',
                            oId: selected.get('periodo_pk'),
                            callback: {
                                success: {
                                    scope: this,
                                    fn: function () {
                                        s.reload();
                                    }
                                }
                            },
                            status_callback: this.status_callback,
                        }).show();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Editando',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Primeiro selecione um item para editar.'
                        });
                },

                recalculate: function (type, possession_group=null) {
                    if (type == 0 || type == 1) {
                        var s = this.getGridFolha().getStore();
                        var selection = this.getGridFolha().getSelectionModel().getSelected();

                        if (selection) {
                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action('GFPControlador', 'get_folha_info'),
                                params: {
                                    pk: selection.get('pk')
                                },
                                success: function (request) {
                                    var obj = Ext.decode(request.responseText);

                                    if (obj.success) {
                                        new toolkit.gfp.RecalculoFolhaPanel({
                                            params: {
                                                ano: obj.ano,
                                                mes: obj.mes,
                                                tipo: obj.tipo_folha
                                            },
                                            payroll: selection.data,
                                            values: { payroll: selection.data.pk },
                                            possession_group: possession_group,
                                        }).show();
                                    }
                                    else {
                                        new toolkit.gfp.RecalculoFolhaPanel({
                                            params: {}
                                        }).show();
                                    }
                                }
                            });
                        }
                        else new toolkit.gfp.RecalculoFolhaPanel({}).show();
                    }
                    else Ext.Msg.show({
                        msg: 'Tipo de recalculo desconhecido!',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },

                summarize: function (type) {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        Ext.Msg.show({
                            msg: 'Tem certeza que deseja processar a folha(' + selection.get('description') + ')?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            scope: this,
                            fn: function (b) {
                                if (b == 'no') return;

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action('GFPPayroll', 'summarize'),
                                    params: {
                                        payroll: selection.get('pk'),
                                        simulate: true
                                    },
                                    success: function (request) {
                                        var obj = Ext.decode(request.responseText);

                                        Ext.Msg.show({
                                            msg: obj.success ? 'Processamento iniciado com sucesso!' : obj.message,
                                            icon: (obj.success ? Ext.Msg.INFO : Ext.Msg.ERROR),
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    failure: function () {
                                        Ext.Msg.show({
                                            msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    scope: this
                                })
                            }
                        });
                    }
                    else
                        Ext.Msg.show({
                            msg: 'Selecione a folha que deseja recalcular!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        })
                },

                consolidate_payroll: function (type) {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        Ext.Msg.show({
                            msg: 'Tem certeza que deseja consolidar a folha(' + selection.get('description') + ')?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            scope: this,
                            fn: function (b) {
                                if (b == 'no') return;

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action('GFPPayroll', 'consolidate_payroll'),
                                    params: {
                                        payroll: selection.get('pk'),
                                    },
                                    success: function (request) {
                                        var obj = Ext.decode(request.responseText);

                                        Ext.Msg.show({
                                            msg: obj.success ? 'Processamento iniciado com sucesso!' : obj.message,
                                            icon: (obj.success ? Ext.Msg.INFO : Ext.Msg.ERROR),
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    failure: function () {
                                        Ext.Msg.show({
                                            msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    scope: this
                                })
                            }
                        });
                    }
                    else
                        Ext.Msg.show({
                            msg: 'Selecione a folha que deseja recalcular!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        })
                },

                copy: function () {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action('GFPControlador', 'get_folha_info'),
                            params: {
                                pk: selection.get('pk')
                            },
                            success: function (request) {
                                var obj = Ext.decode(request.responseText);

                                if (obj.success) {
                                    new toolkit.gfp.CopyPanel({
                                        params: {
                                            base_ano: obj.ano,
                                            base_mes: obj.mes,
                                            base_tipo_folha: obj.tipo_folha
                                        },
                                        payroll: selection.data,
                                    }).show();
                                }
                                else {
                                    new toolkit.gfp.CopyPanel({
                                        params: {}
                                    }).show();
                                }
                            }
                        })
                    }
                    else {
                        new toolkit.gfp.CopyPanel({
                            params: {}
                        }).show();
                    }
                },

                lock_paycheck: function (lock) {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        Ext.Msg.show({
                            msg: 'Tem certeza que deseja bloquear/desbloquear contra-cheque?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            scope: this,
                            fn: function (b) {
                                if (b == 'no') return;

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action('GFPControlador', 'lock_paycheck'),
                                    params: {
                                        pk: selection.get('pk'),
                                        lock: lock
                                    },
                                    success: function (request) {
                                        var obj = Ext.decode(request.responseText);

                                        if (obj.success) s.reload();
                                        else
                                            Ext.Msg.show({
                                                msg: obj.message,
                                                icon: Ext.Msg.ERROR,
                                                buttons: Ext.Msg.OK
                                            })
                                    },
                                    failure: function () {
                                        Ext.Msg.show({
                                            msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    scope: this
                                })
                            }
                        })
                    }
                    else Ext.Msg.show({
                        msg: 'Primeiro selecione uma folha de pagamento.',
                        icon: Ext.Msg.ERROR,
                        scope: this,
                        buttons: Ext.Msg.OK
                    });
                },

                changeStatus: function (status) {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        Ext.Msg.show({
                            msg: 'Tem certeza que deseja mudar o status da folha de pagamento?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            scope: this,
                            fn: function (b) {
                                if (b == 'no') return;

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action('GFPControlador', 'update_status_folha'),
                                    params: {
                                        pk: selection.get('pk'),
                                        status: status
                                    },
                                    success: function (request) {
                                        var obj = Ext.decode(request.responseText);

                                        if (obj.success) s.reload();
                                        else
                                            Ext.Msg.show({
                                                msg: obj.message,
                                                icon: Ext.Msg.ERROR,
                                                buttons: Ext.Msg.OK
                                            })
                                    },
                                    failure: function () {
                                        Ext.Msg.show({
                                            msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    scope: this
                                })
                            }
                        })
                    }
                    else Ext.Msg.show({
                        msg: 'Primeiro selecione uma folha de pagamento.',
                        icon: Ext.Msg.ERROR,
                        scope: this,
                        buttons: Ext.Msg.OK
                    });
                },

                confirmPendencia: function () {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        Ext.Msg.show({
                            msg: 'Tem certeza que deseja confirmar lançamentos da folha de pagamento?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            scope: this,
                            fn: function (b) {
                                if (b == 'no') return;

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action('GFPControlador', 'confirm_pendencia_folha'),
                                    params: {
                                        pk: selection.get('pk')
                                    },
                                    success: function (request) {
                                        var obj = Ext.decode(request.responseText);

                                        if (obj.success) s.reload();
                                        else
                                            Ext.Msg.show({
                                                msg: obj.message,
                                                icon: Ext.Msg.ERROR,
                                                buttons: Ext.Msg.OK
                                            })
                                    },
                                    failure: function () {
                                        Ext.Msg.show({
                                            msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    scope: this
                                })
                            }
                        });
                    }
                    else Ext.Msg.show({
                        msg: 'Primeiro selecione uma folha de pagamento.',
                        icon: Ext.Msg.ERROR,
                        scope: this,
                        buttons: Ext.Msg.OK
                    });
                },

                showManagerPending: function () {
                    var selected = this.getGridFolha().getSelectionModel().getSelected();

                    new rh.gfp.lancador.Pendencies({
                        folha: selected.data
                    }).show()
                },

                applyModel: function () {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action('GFPControlador', 'get_folha_info'),
                            params: { pk: selection.get('pk') },
                            success: function (request) {
                                var obj = Ext.decode(request.responseText);

                                if (obj.success)
                                    new toolkit.gfp.ModeloFolha({
                                        params: {
                                            ano: obj.ano,
                                            mes: obj.mes,
                                            tipo: obj.tipo_folha
                                        }
                                    }).show();
                                else
                                    new toolkit.gfp.ModeloFolha({}).show();
                            },
                            failure: function (request) {
                                Ext.Msg.show({
                                    msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                })
                            },
                            scope: this
                        });
                    }
                    else alert('Primeiro selecione uma Folha de Pagamento.');
                },

                evaluateDifference: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        //                         console.debug(selection.data);
                        new toolkit.gfp.FileGeneratorReturnPayrollGFP(
                            {
                                controller: 'GFPPayroll',
                                action: 'evaluate_differences',
                                payroll: selection.data,
                                title: 'Avaliação de Diferenças'
                            }
                        ).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja avaliar as diferenças!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                evaluateRemunerationBase: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        //                         console.debug(selection.data);
                        new toolkit.gfp.FileGeneratorReturnPayrollGFP(
                            {
                                controller: 'GFPPayroll',
                                action: 'evaluate_remuneration_bases',
                                payroll: selection.data,
                                title: 'Gerar bases de remuneração'
                            }
                        ).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja gerar as bases de remuneração!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                vincularProcessosRRA: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        new toolkit.gfp.CarregarProcessosRRAGFP(
                            {
                                controller: 'GFPPayroll',
                                action: 'vincular_folha_processo_rra',
                                payroll: selection.data,
                                title: 'Vincular processos de RRA'
                            }
                        ).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja gerar vincular os processos RRA!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                editMessage: function () {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action(
                                'GFPControlador',
                                'get_message'
                            ),
                            params: {
                                folha: selection.get('pk')
                            },
                            scope: this,
                            success: function (request) {
                                var obj = Ext.decode(request.responseText);

                                if (obj.success) {
                                    new toolkit.gfp.FolhaMensage({
                                        type: 'POST',
                                        baseParams: {
                                            pk: obj.pk,
                                            folha: obj.folha
                                        },
                                        values: {
                                            texto: obj.texto
                                        }
                                    }).show()
                                }
                                else alert(obj.message)
                            }
                        });
                    }
                    else alert('Primeiro selecione uma Folha de Pagamento.');
                },

                buildBankRelationship: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {

                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/bank_relationship',
                            el: this.getEl(),
                            waitMessage: 'Gerando relatório...',
                            params: {

                                outfile: 'relacaobancaria-' + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                report_name: 'Relação Bancária',
                                folha: selection.get('pk')
                            }

                        });

                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildBankRelationshipPension: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {

                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/bank_relationship_pension',
                            el: this.getEl(),
                            waitMessage: 'Gerando relatório...',
                            params: {

                                outfile: 'relacaobancariapensionista-' + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                report_name: 'Relação Bancária do Pensionista',
                                folha: selection.get('pk')
                            }

                        });

                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildBankRelationshipSimplified: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.RelacaoBancaria({
                            params: {
                                folha: selection.get('pk'),
                                description: selection.get('description')
                            }
                        }).show();


                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildSegregation: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        engine.mq.Report.request({
                            report: '/mt/mpe/gfp/mass_segregation',
                            el: this.getEl(),
                            waitMessage: 'Gerando relatório...',
                            params: {
                                outfile: 'segregacao_de_massa-' + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                report_name: 'Segregação de Massa',
                                folha: selection.get('pk'),
                            }
                        });
                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildConference: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.ConferenciaFolha({
                            params: {
                                folha: selection.get('pk'),
                                folha_anterior: selection.get('folha_anterior'),
                                description: selection.get('description'),
                                types_by_possession_filtered: selection.get('types_by_possession_filtered'),
                            }
                        }).show();
                    }
                    // else new toolkit.gfp.ConferenciaFolha().show();

                    else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildGeneralClassification: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.ClassificacaoGeral({
                            params: {
                                folha: selection.get('pk'),
                                description: selection.get('description'),
                            }
                        }).show();
                    }
                    // else new toolkit.gfp.ClassificacaoGeral().show();

                    else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildGeneralClassificationSynthetic: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.ClassificacaoGeralSintetico({
                            params: {
                                folha: selection.get('pk'),
                                description: selection.get('description'),
                            }
                        }).show();
                    }
                    // else new toolkit.gfp.ClassificacaoGeralSintetico().show();

                    else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildAnalytical: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.AnaliticoFolha({
                            params: {
                                folha: selection.get('pk'),
                                description: selection.get('description'),
                                types_by_possession_filtered: selection.get('types_by_possession_filtered'),
                            }
                        }).show();
                    }
                    // else new toolkit.gfp.AnaliticoFolha().show();

                    else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildABankFile: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.ArquivoBancario({
                            params: {
                                payroll: selection.get('pk'),
                                data_pagamento: selection.get('data_pagamento'),
                                types_by_possession_filtered: selection.get('types_by_possession_filtered'),
                            }
                        }).show();
                    }
                    // else new toolkit.gfp.ArquivoBancario().show();

                    else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                arqBancarioConsig: function () {
                    new toolkit.gfp.ArquivoBancarioConsig().show();
                },

                buildSpPrevcom: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        console.debug(selection.data);
                        new toolkit.gfp.FileGeneratorReturnPayrollGFP({
                            controller: 'GFPSPPrevcom',
                            payroll: selection.data,
                            title: 'Gerador do SP Prevcom'
                        }).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja gerar o arquivo SP Prevcom!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                buildOverview: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {

                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/overview',
                            el: this.getEl(),
                            waitMessage: 'Gerando relatório...',
                            params: {

                                outfile: 'resumogeral-' + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                report_name: 'Resumo Geral',
                                folha: selection.get('pk'),
                            }

                        });

                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildPendencies: function (tipo) {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    var out;
                    var name;
                    if (tipo == 'c') {
                        out = 'pendencias-controle-interno-';
                        name = 'Controle Interno - Pendências';
                    } else {
                        if (tipo == 'fc') {
                            out = 'pendencias-gestao-pessoas-folha-de-pagamento-creditos-';
                        }
                        else {
                            out = 'pendencias-gestao-pessoas-folha-de-pagamento-';
                        }
                        name = 'Gestão de Pessoas - Folha de Pagamento - Pendências'
                    }

                    if (selection) {

                        if (tipo == 'fc') {
                            engine.mq.Report.request({
                                report: '/to/mpe/gfp/paycheck_pending_credits',
                                el: this.getEl(),
                                waitMessage: 'Gerando relatório...',
                                params: {

                                    outfile: out + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                    report_name: name,
                                    folha: selection.get('pk'),

                                }

                            });
                        }
                        else {
                            engine.mq.Report.request({
                                report: '/to/mpe/gfp/paycheck_pending',
                                el: this.getEl(),
                                waitMessage: 'Gerando relatório...',
                                params: {

                                    outfile: out + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                    report_name: name,
                                    folha: selection.get('pk'),
                                    tipo: tipo

                                }

                            });
                        }
                    } else Ext.Msg.show({
                        msg: "Selecione uma folha para gerar o relatório.",
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildCreditPendencies: function (tipo) {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    var out;
                    var name;
                    if (tipo == 'c') {
                        out = 'pendencias-controle-interno-';
                        name = 'Controle Interno - Pendências';
                    } else {
                        out = 'pendencias-gestao-pessoas-folha-de-pagamento-';
                        name = 'Gestão de Pessoas - Folha de Pagamento - Pendências'
                    }

                    if (selection) {

                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/paycheck_pending',
                            el: this.getEl(),
                            waitMessage: 'Gerando relatório...',
                            params: {

                                outfile: out + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                report_name: name,
                                folha: selection.get('pk'),
                                tipo: tipo

                            }

                        });

                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildNLPD: function (finalidade) {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    var out;
                    var name;
                    if (finalidade == 1) {
                        out = 'nota-de-liquidacao-';
                        name = 'Nota de Liquidação';
                    } else {
                        out = 'programa-de-desembolso-';
                        name = 'Programa de Desembolso'
                    }

                    if (selection) {

                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/financialreportpayroll_by_pension_system',
                            el: this.getEl(),
                            waitMessage: 'Gerando relatório...',
                            params: {

                                outfile: out + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                report_name: name,
                                folha: selection.get('pk'),
                                finalidade: finalidade

                            }

                        });

                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildAccountingSummary: function (finalidade) {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {

                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/accounting_summary',
                            el: this.getEl(),
                            waitMessage: 'Gerando relatório...',
                            params: {

                                outfile: 'resumo-contabil-' + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                folha: selection.get('pk'),

                            }

                        });

                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildPrevisionPayment: function () {

                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {

                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/Special_Liquid',
                            el: this.getEl(),
                            waitMessage: 'Gerando relatório...',
                            params: {

                                outfile: 'previsao-pagamento-' + selection.get('tipo_folha') + '-' + selection.get('periodo'),
                                report_name: 'Previsão de pagamento',
                                folha_id: selection.get('pk')
                            }

                        });

                    } else Ext.Msg.show({
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    })
                },

                buildReport: function (report, tipo) {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    var cb = {
                        'GFPNotaLiquidacao': 1,
                        'GFPProgramaDesembolso': 1,
                        'GFPResumoGeral': 1,
                        'GFPRelacaoBancariaLiquidacao': 2,
                        'GFPRelacaoBancariaSimples': 2,
                        'GFPFolhaAnalitico': 2,
                        'GFPChancela': 3
                    };

                    if (selection) {
                        Ext.Ajax.request({
                            url: toolkit.util.Normalize.controller_action('GFPControlador', 'folha_info_report'),
                            params: {
                                pk: selection.get('pk'),
                                tipo: cb[report]
                            },
                            success: function (request) {
                                var obj = Ext.decode(request.responseText);

                                if (obj.success) {
                                    var params = {};

                                    switch (cb[report]) {
                                        case 1:
                                            params = {
                                                folhatipo: obj.folhatipo,
                                                periodo: obj.periodo
                                            };
                                            break;
                                        case 2:
                                            params = {
                                                folhatipo: obj.folhatipo,
                                                ano: obj.ano,
                                                mes: obj.mes
                                            };
                                            break;
                                        case 3:
                                            params = {
                                                folha_tipo: obj.tipo_folha,
                                                periodo: obj.periodo,
                                                tipo: tipo
                                            };
                                            break;
                                        default:
                                            params = {}
                                    }

                                    new toolkit.widget.ExtReportBuild(report).runReport('', params);
                                }
                                else Ext.Msg.show({
                                    msg: obj.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                })
                            },
                            failure: function (request) {
                                Ext.Msg.show({
                                    msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                })
                            },
                            scope: this
                        });
                    }
                    else alert('Primeiro selecione uma Folha de Pagamento.');
                },

                callGeradorArquivoSEFIP: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        console.debug(selection.data);
                        new toolkit.gfp.FileGeneratorReturnPayrollGFP({
                            controller: 'GFPSEFIPFile',
                            payroll: selection.data,
                            title: 'Gerador da SEFIP'
                        }).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja gerar o arquivo SEFIP!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                callGeradorRAIS: function () {
                    new toolkit.gfp.FileGerenatorRAISGFP({ title: 'Gerador da RAIS', controller: 'GFPRAISFile' }).show();
                },

                callReportRelacaoBancariaLiquidacao: function () {
                    this.buildReport('GFPRelacaoBancariaLiquidacao');
                },

                callReportRelacaoBancariaSimples: function () {
                    this.buildReport('GFPRelacaoBancariaSimples');
                },

                buildReportResumoEventosGeral: function () {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.ResumoGeralEvento({
                            params: {
                                folha: selection.get('pk'),
                                description: selection.get('description')
                            }
                        }).show();
                    }
                    else new toolkit.gfp.ResumoGeralEvento().show();
                },

                buildReportServidoresPorConsignacaoTipo: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.ServidoresPorConsignacaoTipo({
                            params: {
                                folha: selection.get('pk'),
                                // description: selection.get('description')
                            }
                        }).show();
                    }
                    else new toolkit.gfp.ServidoresPorConsignacaoTipo().show();
                },

                buildReportResumoEventosConsignatario: function () {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        new toolkit.gfp.ResumoGeralEventoConsignatario({
                            params: {
                                folha: selection.get('pk'),
                                description: selection.get('description')
                            }
                        }).show();
                    }
                    else new toolkit.gfp.ResumoGeralEventoConsignatario().show();
                },

                buildReportMargem: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/consignable_margin',
                            el: this.getEl(),
                            waitMessage: 'Gerando os documentos...',
                            params: {
                                outfile: 'relatorio-margem-consignada-' + selection.get('description'),
                                report_name: 'Relatório de Margem Confignada ' + selection.get('description'),
                                folha: selection.get('pk'),
                            }
                        });
                    } else {
                        Ext.Msg.show({
                            'title': 'Atenção',
                            'icon': Ext.Msg.INFO,
                            'buttons': Ext.Msg.OK,
                            'msg': 'Selecione pelo menos um item.'
                        });
                    }
                },

                buildReportContrachequeInibido: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        engine.mq.Report.request({
                            report: '/to/mpe/gfp/Listagem_de_Contracheques_Inibidos',
                            el: this.getEl(),
                            waitMessage: 'Gerando os documentos...',
                            params: {
                                outfile: 'relatorio-contrachequeinibido-' + selection.get('description'),
                                report_name: 'GFPContrachequeInibido ' + selection.get('description'),
                                tipo_folha: selection.get('tipo_folha'),
                                folha: selection.get('pk'),
                            }
                        });
                    } else {
                        Ext.Msg.show({
                            'title': 'Atenção',
                            'icon': Ext.Msg.INFO,
                            'buttons': Ext.Msg.OK,
                            'msg': 'Selecione pelo menos um item.'
                        });
                    }
                },

                buildDirf: function () {
                    new Ext.Window({
                        title: 'Gerador da DIRF',
                        closable: true,
                        resizable: false,
                        width: 560,
                        modal: true,
                        border: false,
                        items: new toolkit.gfp.dirf.Gerador()
                    }).show();
                },

                buildIgeprev: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection)
                        new toolkit.rh.gfp.paycheck.socialsecurity.WindowFileGenerator({ sheet: selection.get('pk') }).show();
                    else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja gerar o arquivo do IGEPREV!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                buildSisprev: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection)
                    new toolkit.gfp.FileGeneratorReturnPeriodGFP({
                        controller: 'GFPSisprevGenerator',
                        period: { pk: selection.data.periodo_pk },
                        title: 'Gerador de arquivo IGEPREV (Sisprev)'
                    }).show();
                    else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja gerar o arquivo do IGEPREV!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                loadFile: function () {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection)
                        new toolkit.gfp.LoaderFileGFP({ payroll: selection.data }).show();
                    else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja carregar o arquivo de lançamentos!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                generateReturnViabillizeFiles: function (controller, action) {
                    // var selection = this.getGridFolha().getSelectionModel().getSelected();
                    // new toolkit.gfp.FileGeneratorReturnPeriodGFP({
                    //     controller: 'GFPReturnViabillize',
                    //     title: 'Gerador de arquivo retorno do Viabillize'
                    // }).show();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        console.debug(selection.data);
                        new toolkit.gfp.FileGeneratorReturnPayrollGFP({
                            controller: 'GFPReturnViabillize',
                            payroll: selection.data,
                            title: 'Gerador de arquivo retorno do Viabillize'
                        }).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja carregar o arquivo de lançamentos!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                generateReturnPlansaudeFiles: function (controller, action) {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        console.debug(selection);
                        new toolkit.gfp.FileGeneratorReturnPeriodGFP({
                            controller: 'GFPReturnPlansaude',
                            period: { pk: selection.data.periodo_pk },
                            title: 'Gerador de arquivo retorno do Plansaúde'
                        }).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Selecione uma folha do período desejado!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                generateReturnNeoConsigFiles: function (controller, action) {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        console.debug(selection);
                        new toolkit.gfp.FileGeneratorReturnPeriodGFP({
                            controller: 'GFPNeoConsigInitial',
                            period: { pk: selection.data.periodo_pk },
                            title: 'Gerador de arquivo retorno do NeoConsig'
                        }).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Selecione uma folha do período desejado!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                generateReturnConsigFacilFiles: function (controller, action) {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        console.debug(selection);
                        new toolkit.gfp.FileGeneratorReturnPeriodGFP({
                            controller: 'GFPConsigFacilInitial',
                            period: { pk: selection.data.periodo_pk },
                            title: 'Gerador de arquivo retorno do ConsigFácil'
                        }).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Selecione uma folha do período desejado!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                generateFPS900File: function (controller, action) {
                    var selection = this.getGridFolha().getSelectionModel().getSelected();
                    if (selection) {
                        console.debug(selection.data);
                        new toolkit.gfp.FileGeneratorReturnPayrollGFP({
                            controller: 'GFPPasepFps900',
                            payroll: selection.data,
                            title: 'Gerador de arquivo PIS [FPS900]'
                        }).show();
                    } else
                        Ext.Msg.show({
                            msg: 'Primeiro selecione a folha para a qual deseja carregar o arquivo de lançamentos!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                },

                getActions: function () {
                    if (!this.actions)
                        this.actions = [
                            [
                                {
                                    text: 'Nova',
                                    iconCls: 'icon-core icon-core-add',
                                    scope: this,
                                    handler: this.create
                                }, {
                                    text: 'Editar',
                                    iconCls: 'icon-core icon-core-edit',
                                    scope: this,
                                    handler: this.edit
                                },
                                '-',
                                {
                                    text: 'Editar Periodo',
                                    scope: this,
                                    handler: this.editPeriodo
                                },
                                '-',
                                {
                                    text: 'Bloquear/Desbloquear Contracheques',
                                    menu: [
                                        {
                                            text: 'Bloquear Contracheques',
                                            scope: this,
                                            iconCls: 'icon-fopag icon-closed-padlock',
                                            handler: function () { this.lock_paycheck(true) }
                                        },
                                        {
                                            text: 'Desbloquear Contracheques',
                                            scope: this,
                                            iconCls: 'icon-fopag icon-open-padlock',
                                            handler: function () { this.lock_paycheck(false) }
                                        },
                                    ]
                                },
                                '-',
                                {
                                    text: 'Processar Folha de Pagamento',
                                    scope: this,
                                    handler: this.summarize,
                                    iconCls: 'icon-fopag icon-stamp-arrow'
                                }, {
                                    text: 'Consolidar Folha de Pagamento',
                                    scope: this,
                                    handler: this.consolidate_payroll,
                                    iconCls: 'icon-fopag icon-medal-arrow'
                                },
                                {
                                    text: 'Recalcular Folha de Pagamento',
                                    scope: this,
                                    iconCls: 'icon-fopag icon-compile',
                                    menu: [
                                        {
                                            text: 'Recalcular Todos',
                                            scope: this,
                                            handler: function () { this.recalculate(0) }
                                        },
                                        {
                                            text: 'Recalcular Membros',
                                            scope: this,
                                            handler: function () { this.recalculate(0, 'membros') }
                                        },
                                        {
                                            text: 'Recalcular Servidores',
                                            scope: this,
                                            handler: function () { this.recalculate(0, 'servidores') }
                                        },
                                        {
                                            text: 'Recalcular Comissionados',
                                            scope: this,
                                            handler: function () { this.recalculate(0, 'comissionados') }
                                        },
                                        {
                                            text: 'Recalcular Estagiários',
                                            scope: this,
                                            handler: function () { this.recalculate(0, 'estagiarios') }
                                        },
                                        {
                                            text: 'Recalcular Residentes',
                                            scope: this,
                                            handler: function () { this.recalculate(0, 'residentes') }
                                        },
                                        {
                                            text: 'Recalcular Aposentados',
                                            scope: this,
                                            handler: function () { this.recalculate(0, 'aposentados') }
                                        },
                                        {
                                            text: 'Recalcular Pensionistas',
                                            scope: this,
                                            handler: function () { this.recalculate(0, 'pensionistas') }
                                        },
                                        {
                                            text: 'Recalcular Adidos',
                                            scope: this,
                                            handler: function () { this.recalculate(0, 'adidos') }
                                        },
                                    ]
                                    // handler: function () { this.recalculate(0)}
                                }, {
                                    text: 'Avaliar Diferenças',
                                    iconCls: 'icon-fopag icon-task-select',
                                    scope: this,
                                    handler: this.evaluateDifference
                                },
                                {
                                    text: 'Copiar Folha de Pagamento',
                                    iconCls: true,
                                    scope: this,
                                    iconCls: 'icon-fopag icon-arrow-repeat',
                                    handler: this.copy
                                }, {
                                    text: 'Mensagem do Contra Cheque',
                                    handler: this.editMessage,
                                    iconCls: 'icon-esocial icon-balloon-exclamation',
                                    scope: this
                                }, {
                                    text: 'Copiar Contas de Crédito',
                                    scope: this,
                                    handler: function () {
                                        new toolkit.gfp.CopyContaCredito().show()
                                    }
                                }, {
                                    text: 'Mudar status',
                                    menu: [
                                        {
                                            text: 'Em produção',
                                            scope: this,
                                            iconCls: '',
                                            handler: function () { this.changeStatus(1) }
                                        },
                                        {
                                            text: 'Em analise',
                                            scope: this,
                                            iconCls: '',
                                            handler: function () { this.changeStatus(2) }
                                        },
                                        {
                                            text: 'Processado',
                                            scope: this,
                                            iconCls: 'icon-fopag icon-stamp-arrow',
                                            handler: function () { this.changeStatus(4) }
                                        },
                                        {
                                            text: 'Fechado',
                                            scope: this,
                                            iconCls: 'icon-fopag icon-closed-padlock',
                                            handler: function () { this.changeStatus(3) }
                                        }
                                    ]
                                }, {
                                    text: 'Confirmar Pendencias',
                                    iconCls: true,
                                    scope: this,
                                    handler: this.confirmPendencia
                                }, {
                                    text: 'Gestor de Pendencias',
                                    iconCls: true,
                                    scope: this,
                                    handler: this.showManagerPending
                                }, {

                                    text: 'Gerar bases de remuneração',
                                    scope: this,
                                    handler: this.evaluateRemunerationBase
                                },
                                {

                                    text: 'Vincular processos de RRA',
                                    scope: this,
                                    handler: this.vincularProcessosRRA
                                },
                                '-',
                                {
                                    text: 'Relatórios',
                                    menu: [
                                        {
                                            text: 'Segregação de Massa',
                                            scope: this,
                                            handler: this.buildSegregation
                                        },
                                        {
                                            text: 'Conferência de Folha de Pagamento',
                                            scope: this,
                                            handler: this.buildConference
                                        },
                                        {
                                            text: 'Classificação Geral',
                                            menu: [
                                                {
                                                    text: 'Analítico',
                                                    scope: this,
                                                    handler: this.buildGeneralClassification
                                                },
                                                {
                                                    text: 'Sintético',
                                                    scope: this,
                                                    handler: this.buildGeneralClassificationSynthetic
                                                },
                                            ]
                                        },
                                        {
                                            text: 'Analitico da Folha de Pagamento',
                                            scope: this,
                                            handler: this.buildAnalytical
                                        },
                                        {
                                            text: 'Resumo Geral da Folha',
                                            scope: this,
                                            handler: this.buildOverview
                                        },
                                        {
                                            text: 'Resumo de Evento',
                                            menu: [
                                                {
                                                    text: 'por Evento',
                                                    scope: this,
                                                    handler: this.buildReportResumoEventosGeral
                                                },
                                                {
                                                    text: 'por Consignatário',
                                                    scope: this,
                                                    handler: this.buildReportResumoEventosConsignatario
                                                }
                                            ]
                                        },
                                        {
                                            text: 'Relação Bancaria',
                                            menu: [
                                                {
                                                    text: 'Liquidação',
                                                    scope: this,
                                                    handler: this.buildBankRelationship
                                                },
                                                {
                                                    text: 'Simples',
                                                    scope: this,
                                                    handler: this.buildBankRelationshipSimplified
                                                },
                                                {
                                                    text: 'Liquido de Pensão',
                                                    scope: this,
                                                    handler: this.buildBankRelationshipPension
                                                }
                                            ]
                                        },
                                        // {
                                        //     text: 'Relação Bancaria',
                                        //     scope: this,
                                        //     handler: function() { this.buildReport('GFPRelacaoBancaria') }
                                        // },
                                        '-',
                                        {
                                            text: 'Nota de Liquidação',
                                            scope: this,
                                            handler: function () { this.buildNLPD(1) }
                                        },
                                        {
                                            text: 'Programa de Desembolso',
                                            scope: this,
                                            handler: function () { this.buildNLPD(2) }
                                        },
                                        {
                                            text: 'Resumo Contábil',
                                            scope: this,
                                            handler: function () { this.buildAccountingSummary() }
                                        },
                                        '-',
                                        {
                                            text: 'Previsão de Pagamento',
                                            scope: this,
                                            handler: this.buildPrevisionPayment
                                        },
                                        '-',
                                        {
                                            text: 'Relatório de margem Consignada',
                                            scope: this,
                                            handler: this.buildReportMargem
                                        },
                                        '-',
                                        {
                                            text: 'Lançamentos a serem validados',
                                            menu: [
                                                {
                                                    text: 'pela Folha de Pagamento',
                                                    menu: [
                                                        {
                                                            text: 'Conferência geral',
                                                            scope: this,
                                                            handler: function () { this.buildPendencies('f') }
                                                        },
                                                        {
                                                            text: 'Conferência créditos',
                                                            scope: this,
                                                            handler: function () { this.buildPendencies('fc') }
                                                        }
                                                    ]
                                                },
                                                {
                                                    text: 'pelo Controle Interno',
                                                    scope: this,
                                                    handler: function () { this.buildPendencies('c') }
                                                }
                                            ]
                                        },
                                        '-',
                                        {
                                            text: 'Contracheque Inibido',
                                            scope: this,
                                            handler: this.buildReportContrachequeInibido
                                        },
                                        '-',
                                        {
                                            text: 'Servidores por evento e tipo',
                                            scope: this,
                                            handler: this.buildReportServidoresPorConsignacaoTipo
                                        },
                                    ]
                                },
                                '-',
                                {
                                    text: 'Carregamento de arquivos',
                                    handler: this.loadFile,
                                    scope: this
                                },
                                '-',
                                {
                                    text: 'Geração de Arquivos',
                                    menu: [
                                        {
                                            text: 'Arquivos Bancários',
                                            scope: this,
                                            handler: this.buildABankFile
                                        },
                                        {
                                            text: 'Arquivos Bancários - Consignados',
                                            scope: this,
                                            handler: this.arqBancarioConsig
                                        },
                                        {
                                            text: 'SP Prevcom',
                                            scope: this,
                                            handler: this.buildSpPrevcom
                                        },
                                        {
                                            text: 'Previdência Social',
                                            scope: this,
                                            menu: [
                                                {
                                                    text: 'IGEPREV',
                                                    scope: this,
                                                    handler: this.buildIgeprev
                                                },
                                                {
                                                    text: 'IGEPREV (Sisprev)',
                                                    scope: this,
                                                    handler: this.buildSisprev
                                                },
                                                {
                                                    text: 'INSS',
                                                    disabled: true
                                                },
                                                {
                                                    text: 'PREVPALMAS',
                                                    disabled: true
                                                },
                                                {
                                                    text: 'IPASGO',
                                                    disabled: true
                                                }
                                            ]
                                        },
                                        {
                                            text: 'Imposto Retido na Fonte',
                                            scope: this,
                                            handler: this.buildDirf
                                        },
                                        {
                                            text: 'Arquivo SEFIP',
                                            scope: this,
                                            handler: this.callGeradorArquivoSEFIP
                                        },
                                        {
                                            text: 'Relação Anual de Informações Sociais',
                                            scope: this,
                                            handler: this.callGeradorRAIS
                                        }, {
                                            text: 'PASEP',
                                            scope: this,
                                            menu: [
                                                {
                                                    text: 'FPS900',
                                                    scope: this,
                                                    handler: this.generateFPS900File
                                                },
                                            ]
                                        },
                                        '-', {
                                            text: 'Retorno Viabillize',
                                            handler: this.generateReturnViabillizeFiles,
                                            scope: this
                                        }, {
                                            text: 'Retorno Plansaúde',
                                            handler: this.generateReturnPlansaudeFiles,
                                            scope: this
                                        }, {
                                            text: 'Retorno NeoConsig',
                                            handler: this.generateReturnNeoConsigFiles,
                                            scope: this
                                        },{
                                            text: 'Retorno ConsigFácil',
                                            handler: this.generateReturnConsigFacilFiles,
                                            scope: this
                                        },
                                        '-',
                                        {
                                            text: 'Demonstrativo IGEPREV',
                                            scope: this,
                                            handler: function () {
                                                Ext._create('rh.gfp.reports.DemonstrativoIgeprevWindow').show();
                                            }
                                        },
                                    ]
                                },
                                {
                                    text: 'Importação de Diárias',
                                    scope: this,
                                    handler: this.callImportPayrollWindow
                                },
                                {
                                    text: 'Importação de Prestadores Eventuais',
                                    scope: this,
                                    handler: this.callImportEventualProvider
                                }
                            ]
                        ];

                    return this.actions;
                },

                callImportEventualProvider: function (type) {
                    var s = this.getGridFolha().getStore();
                    var selection = this.getGridFolha().getSelectionModel().getSelected();

                    if (selection) {
                        Ext.Msg.show({
                            msg: 'Tem certeza que deseja importar lançamentos de Prestadores Eventuais para a folha (' + selection.get('description') + ')?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            scope: this,
                            fn: function (b) {
                                if (b == 'no') return;

                                Ext.Ajax.request({
                                    url: toolkit.util.Normalize.controller_action('DEFINPFProviderEntryRestful', 'import_eventual_provider'),
                                    params: {
                                        payroll: selection.get('pk')
                                    },
                                    success: function (request) {
                                        var obj = Ext.decode(request.responseText);

                                        Ext.Msg.show({
                                            msg: obj.success ? 'Processamento iniciado com sucesso!' : obj.message,
                                            icon: (obj.success ? Ext.Msg.INFO : Ext.Msg.ERROR),
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    failure: function () {
                                        Ext.Msg.show({
                                            msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        })
                                    },
                                    scope: this
                                })
                            }
                        });
                    }
                    else
                        Ext.Msg.show({
                            msg: 'Selecione a folha que deseja importar!',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        })
                },

                callImportPayrollWindow: function () {
                    Ext._create('toolkit.rh.gfp.payroll.ImportPayroll.Window').show();
                },

                getGridToolbar: function () {
                    if (!this.gridToolbar) {
                        this.gridToolbar = new Ext.Toolbar({
                            items: [
                                {
                                    text: 'Folha de Pagamento',
                                    iconCls: true,
                                    icon: '/' + global.Context + '/static/rh/images/folha-de-pagamento.png',
                                    split: true,
                                    defaultStyle: 'splitbutton',
                                    menu: this.getActions()
                                },
                                '-',
                                '->',
                                '-',
                                {
                                    xtype: 'combo',
                                    store: [
                                        [0, 'TODOS'],
                                        [1, 'EM PRODUÇÃO'],
                                        [2, 'EM ANALISE'],
                                        [4, 'PROCESSADA'],
                                        [3, 'FINALIZADA'],
                                    ],
                                    emptyText: 'Status para filtro',
                                    width: 140,
                                    triggerAction: 'all',
                                    listeners: {
                                        scope: this,
                                        select: function (combo, record) {
                                            var store = this.getGridFolha().getStore();

                                            if (record.get('field1') != 0)
                                                store.baseParams['status'] = record.get('field1');
                                            else
                                                delete store.baseParams['status'];

                                            store.load({});
                                        }
                                    }
                                },
                                '-',
                                {
                                    xtype: 'combo',
                                    store: new Ext.data.JsonStore({
                                        proxy: new Ext.data.HttpProxy({
                                            url: toolkit.util.Normalize.controller_action('GFPControlador', 'anos_folha'),
                                            disableCaching: true,
                                            method: 'GET'
                                        }),
                                        root: 'root',
                                        fields: ['pk', 'description']
                                    }),
                                    displayField: 'description',
                                    valueFeild: 'pk',
                                    emptyText: 'Ano para filtro',
                                    width: 140,
                                    triggerAction: 'all',
                                    listeners: {
                                        scope: this,
                                        select: function (combo, record) {
                                            var store = this.getGridFolha().getStore();

                                            if (record.get('pk') != 0)
                                                store.baseParams['periodo__ano'] = record.get('pk');
                                            else
                                                delete store.baseParams['periodo__ano'];

                                            store.load({});
                                        }
                                    }
                                },
                                '-',
                                {
                                    xtype: 'combo',
                                    store: [
                                        [0, 'TODOS'],
                                        [1, 'JANEIRO'],
                                        [2, 'FEVEREIRO'],
                                        [3, 'MARÇO'],
                                        [4, 'ABRIL'],
                                        [5, 'MAIO'],
                                        [6, 'JUNHO'],
                                        [7, 'JULHO'],
                                        [8, 'AGOSTO'],
                                        [9, 'SETEMBRO'],
                                        [10, 'OUTUBRO'],
                                        [11, 'NOVEMBRO'],
                                        [12, 'DEZEMBRO'],
                                        [13, '13º SALÁRIO'],
                                    ],
                                    emptyText: 'Mês para filtro',
                                    width: 140,
                                    triggerAction: 'all',
                                    listeners: {
                                        scope: this,
                                        select: function (combo, record) {
                                            var store = this.getGridFolha().getStore();

                                            if (record.get('field1') != 0)
                                                store.baseParams['periodo__mes'] = record.get('field1');
                                            else
                                                delete store.baseParams['periodo__mes'];

                                            store.load({});
                                        }
                                    }
                                },
                                '-',
                                {
                                    xtype: 'combo',
                                    store: new Ext.data.JsonStore({
                                        proxy: new Ext.data.HttpProxy({
                                            url: toolkit.util.Normalize.controller_action('GFPControlador', 'tipos_folha'),
                                            disableCaching: true,
                                            method: 'GET'
                                        }),
                                        root: 'root',
                                        fields: ['pk', 'description']
                                    }),
                                    displayField: 'description',
                                    valueFeild: 'pk',
                                    emptyText: 'Tipo de folha para filtro',
                                    width: 140,
                                    triggerAction: 'all',
                                    listeners: {
                                        scope: this,
                                        select: function (combo, record) {
                                            var store = this.getGridFolha().getStore();

                                            if (record.get('pk') != 0)
                                                store.baseParams['tipo_folha'] = record.get('pk');
                                            else
                                                delete store.baseParams['tipo_folha'];

                                            store.load({});
                                        }
                                    }
                                },
                            ]
                        });
                    }

                    return this.gridToolbar;
                },

                getGridFolha: function () {
                    if (!this.gridFolha) {
                        var store = new Ext.data.JsonStore({
                            url: toolkit.util.Normalize.controller_action('GFPControlador', 'folhas'),
                            fields: [
                                'pk', 'description', 'status', 'tipo_folha', 'periodo', 'periodo_pk',
                                'data_pagamento', 'pendencia_folha', 'complement', 'servidores',
                                'pendencia_controle', 'validado_por', 'fechado_por', 'processado_por',
                                'paycheck_locked', 'types_by_possession_filtered', 'folha_anterior'
                            ],
                            root: 'root',
                            totalProperty: 'totalRows'
                        });

                        this.gridFolha = new Ext.grid.GridPanel({
                            listeners: {
                                scope: this,
                                dblclick: this.edit,
                                render: function (g) {

                                    new Ext.LoadMask(
                                        g.getEl(),
                                        {
                                            msg: 'Corregando dados da folha de pagamento...',
                                            store: g.getStore()
                                        }
                                    );

                                    g.getStore().load({});
                                }
                            },
                            border: false,
                            bbar: new Ext.PagingToolbar({
                                store: store,
                                displayInfo: true,
                                pageSize: 30
                            }),
                            autoExpandColumn: 'periodo',
                            tbar: this.getGridToolbar(),
                            cm: new Ext.grid.ColumnModel([
                                {
                                    dataIndex: 'status',
                                    id: 'status',
                                    width: 45,
                                    menuDisabled: true,
                                    renderer: function (value) { return toolkit.util.formatStatus(value, 'gfp-icon-correct'); }
                                }, {
                                    dataIndex: 'tipo_folha',
                                    header: 'Tipo de Folha',
                                    width: 160,
                                    sortable: true
                                }, {
                                    dataIndex: 'complement',
                                    header: 'Complemento',
                                    width: 100
                                }, {
                                    dataIndex: 'periodo',
                                    id: 'periodo',
                                    header: 'Periodo',
                                    width: 140,
                                    sortable: true
                                }, {
                                    dataIndex: 'data_pagamento',
                                    header: 'Pagamento em',
                                    width: 100
                                }, {
                                    dataIndex: 'fechado_por',
                                    header: 'Fechado',
                                    width: 170
                                }, {
                                    dataIndex: 'processado_por',
                                    header: 'Processado',
                                    width: 170
                                }, {
                                    dataIndex: 'pendencia_folha',
                                    header: 'Folha',
                                    width: 125,
                                    renderer: function (value) { return '<p style="text-align:right">' + value + ' pendencia(s)</p>' }
                                }, {
                                    dataIndex: 'pendencia_controle',
                                    header: 'Cont. Interno',
                                    width: 125,
                                    renderer: function (value) { return '<p style="text-align:right">' + value + ' pendencia(s)</p>' }
                                }, {
                                    dataIndex: 'paycheck_locked',
                                    header: 'C. Bloqueado ?',
                                    width: 45,
                                    renderer: function (value) {
                                        var variavel = value
                                        return (value ? 'Sim' : 'Não');
                                    }
                                }
                            ]),
                            store: store
                        });
                    }

                    return this.gridFolha;
                },

                constructor: function () {
                    var cf = {
                        title: 'Controlador da Folha',
                        closable: true,
                        layout: 'fit',
                        border: false,
                        items: this.getGridFolha()
                    };

                    toolkit.gfp.Controlador.superclass.constructor.call(this, cf);

                    var ts = toolkit.Application.tabspace;
                    ts.remove(ts.getActiveTab());
                    ts.add(this);
                    ts.setActiveTab(this);
                }
            }
        )
    }
);
