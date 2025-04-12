Ext._define('raf.functionalactivityreport.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.functionalactivityreport.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'search', '->', 'download', '-', '->', 'manage', 'report'],

    sendEdoc: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;

        if(year && month) {
            console.log(year + ' ' +month);
            this.openSendEdocWindow(month, year)
        } else {
            Ext.Msg.show({
                title: 'Erro',
                msg: 'Selecione o ano e o mês.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    openSendEdocWindow: function(month, year) {
        Ext._create('raf.management.SendEdocWindow', {
            params: {
                month: month,
                year: year
            },
            managementGroupGrid: this.managementGroupGrid,
        }).show();
    },

    openRaf: function() {
        var selected = this.getSelectionModel().getSelected();
        var rest = Ext._create('raf.functionalactivityreport.Restful');

        if(selected) {

            Ext.Msg.show({
                title: 'Abrir RAF',
                msg: 'Tem certeza que deseja abrir o RAF selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;

                    rest.openRaf(
                        selected.get('pk'),
                        {
                            scope: this,
                            fn: function(rst) {
                                core.invokeCallback((this.callback || {}).success);
                                this.getStore().reload();

                                Ext.Msg.show({
                                    title: 'Abrir RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: 'Abrir RAF',
                                    msg: message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function() {}
                        }
                    );
                }
            });

        } else {
            Ext.Msg.show({
                title: 'Abrir RAF',
                msg: 'Primeiro selecione o RAF que deseja abrir.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }

    },

    closeRaf: function() {
        var selected = this.getSelectionModel().getSelected();
        var rest = Ext._create('raf.functionalactivityreport.Restful');

        if(selected) {

            Ext.Msg.show({
                title: 'Fechar RAF',
                msg: 'Tem certeza que deseja fechar o RAF selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;

                    rest.closeRaf(
                        selected.get('pk'),
                        {
                            scope: this,
                            fn: function(rst) {
                                core.invokeCallback((this.callback || {}).success);
                                this.getStore().reload();

                                Ext.Msg.show({
                                    title: 'Fechar RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: 'Fechar RAF',
                                    msg: message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function() {}
                        }
                    );
                }
            });

        } else {
            Ext.Msg.show({
                title: 'Abrir RAF',
                msg: 'Primeiro selecione o RAF que deseja fechar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }

    },

    openAllRaf: function() {
      var month = this.getParams().month;
      var year = this.getParams().year;
      var raf = month+'.'+year;
      var rest = Ext._create('raf.functionalactivityreport.Restful');
      if(month && year) {
          Ext.Msg.show({
              title: 'Abrir RAF',
              msg: 'Tem certeza que deseja abrir todos os RAFs do mês selecionado?',
              icon: Ext.Msg.QUESTION,
              buttons: Ext.Msg.YESNO,
              scope: this,
              fn: function(btn) {
                  if(btn=='no') return;
                  rest.openAllRaf(
                      raf,
                      {
                          scope: this,
                          fn: function(rst) {
                              core.invokeCallback((this.callback || {}).success);
                              this.getStore().reload();

                              Ext.Msg.show({
                                  title: 'Abrir RAF',
                                  msg: rst.message,
                                  icon: Ext.Msg.INFO,
                                  buttons: Ext.Msg.OK
                              });
                          }
                      },
                      {
                          scope: this,
                          fn: function(message) {
                              Ext.Msg.show({
                                  title: 'Abrir RAF',
                                  msg: message,
                                  icon: Ext.Msg.ERROR,
                                  buttons: Ext.Msg.OK
                              });
                          }
                      },
                      {
                          scope: this,
                          fn: function() {}
                      }
                  );
              }
          });
      } else {
          Ext.Msg.show({
              title: 'Abrir RAF',
              msg: 'Primeiro selecione o mês que deseja abrir.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
          });
      }
    },

    closeAllRaf: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var raf = month+'.'+year;
        var rest = Ext._create('raf.functionalactivityreport.Restful');
        if(month && year) {
            Ext.Msg.show({
                title: 'Fechar RAF',
                msg: 'Tem certeza que deseja fechar todos os RAFs do mês selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    rest.closeAllRaf(
                        raf,
                        {
                            scope: this,
                            fn: function(rst) {
                                core.invokeCallback((this.callback || {}).success);
                                this.getStore().reload();

                                Ext.Msg.show({
                                    title: 'Fechar RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: 'Fechar RAF',
                                    msg: message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function() {}
                        }
                    );
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Fechar RAF',
                msg: 'Primeiro selecione o mês que deseja fechar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    openCreateRAFWindow: function() {
        Ext._create('raf.management.CreateRAFWindow', {
            values: { },
            managementGroupGrid: this.managementGroupGrid,
        }).show();
    },

    openDropRAFWindow: function() {
        Ext._create('raf.management.DropRAFWindow', {
            values: { },
        }).show();
    },

    dropRAF: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            employee = selected.get('employee');
        } else {
            employee = '';
        }
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Removendo RAF(s)...'});
        if(month && year) {
            Ext.Msg.show({
                title: 'Remover RAF',
                msg: 'Tem certeza que deseja remover o(s) RAF(s) selecionado(s)?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('RAFFunctionalActivityReport', 'dropRAF'),
                        callback: function() {
                            this.managementGroupGrid.getStore().reload();
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Remover RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            } else {
                                Ext.Msg.show({
                                    title: 'Remover RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                            core.invokeCallback((this.callback || {}).success);
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Remover RAF',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {
                            month: month,
                            year: year,
                            employee: employee
                        },
                    });
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Remover RAF',
                msg: 'Primeiro selecione o RAF que deseja remover.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    processRAF: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            employee = selected.get('employee');
        } else {
            employee = '';
        }
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando RAF(s)...'});
        if(month && year) {
            Ext.Msg.show({
                title: 'Processar RAF',
                msg: 'Tem certeza que deseja processar o(s) RAF(s) selecionado(s)?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('RAFFunctionalActivityReport', 'processRAF'),
                        callback: function() {
                            this.managementGroupGrid.getStore().reload();
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Processar RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            } else {
                                Ext.Msg.show({
                                    title: 'Processar RAF',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                            core.invokeCallback((this.callback || {}).success);
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Processar RAF',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {
                            month: month,
                            year: year,
                            employee: employee
                        },
                    });
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Processar RAF',
                msg: 'Primeiro selecione o(s) RAF(s) que deseja processar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    recalculateBalanceRAF: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            employee = selected.get('employee');
            msgs = 'Tem certeza que deseja <b>Recalcular os SALDOS</b> do RAF de <b>' + month + '/' + year + '</b>, para <b>' + selected.get('employee_unicode') + '</b>?';
        } else {
            employee = null;
            msgs = 'Tem certeza que deseja <b>Recalcular TODOS os SALDOS</b> do RAF de <b>' + month + '/' + year + '</b>?';
        }
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando RAF(s)...'});
        console.log(employee);
        // if(month && year && selected) {
        if(month && year) {
            Ext.Msg.show({
                title: 'Recalcular SALDOS',
                msg: msgs,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('RAFFunctionalActivityReport', 'recalculateBalanceRAF'),
                        callback: function() {
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            if (rst.success == true) {
                                Ext.Msg.show({
                                    title: 'Recalcular SALDOS',
                                    msg: rst.message,
                                    icon: Ext.Msg.INFO,
                                    buttons: Ext.Msg.OK
                                });
                            } else {
                                Ext.Msg.show({
                                    title: 'Recalcular SALDOS',
                                    msg: rst.message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                            core.invokeCallback((this.callback || {}).success);
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Recalcular SALDOS',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {
                            month: month,
                            year: year,
                            employee: employee
                        },
                    });
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Recalcular SALDOS',
                msg: 'Primeiro selecione o RAF que deseja recalcular.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    openImportEproc2AthenasWindow: function() {
        Ext._create('raf.management.ImportEproc2AthenasWindow', {
            values: { },
        }).show();
    },

    dropEproc2AthenasWindow: function() {
        Ext._create('raf.management.DropEproc2AthenasWindow', {
            values: { },
        }).show();
    },

    openImportEExt2AthenasWindow: function() {
        Ext._create('raf.management.ImportEExt2AthenasWindow', {
            values: { },
        }).show();
    },

    dropEExt2AthenasWindow: function() {
        Ext._create('raf.management.DropEExt2AthenasWindow', {
            values: { },
        }).show();
    },

    addWorkerlocation: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if (selected.get('submitted') == false) {
                if (selected.get('closed') == false) {
                    Ext._create('raf.management.AddWorkerlocationWindow', {
                        values: {
                            'month_reference': '<b>' + this.getParams().month + '/' + this.getParams().year + '</b>',
                            'employee': '<b>' + selected.get('employee_unicode') + '</b>',
                        },
                        raf: selected.get('pk'),
                    }).show();
                } else {
                    Ext.Msg.show({
                        title: 'Editar RAF',
                        msg: 'O RAF encontra-se fechado, edição não permitida.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            } else {
                Ext.Msg.show({
                    title: 'Editar RAF',
                    msg: 'O RAF encontra-se submetido, edição não permitida.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Editar RAF',
                msg: 'Primeiro selecione o RAF no qual deseja editar os Órgãos de Execução.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    delWorkerlocation: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            if (selected.get('submitted') == false) {
                if (selected.get('closed') == false) {
                    Ext._create('raf.management.DelWorkerlocationWindow', {
                        values: {
                            'month_reference': '<b>' + this.getParams().month + '/' + this.getParams().year + '</b>',
                            'employee': '<b>' + selected.get('employee_unicode') + '</b>',
                        },
                        raf: selected.get('pk'),
                    }).show();
                } else {
                    Ext.Msg.show({
                        title: 'Editar RAF',
                        msg: 'O RAF encontra-se fechado, edição não permitida.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            } else {
                Ext.Msg.show({
                    title: 'Editar RAF',
                    msg: 'O RAF encontra-se submetido, edição não permitida.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        } else {
            Ext.Msg.show({
                title: 'Editar RAF',
                msg: 'Primeiro selecione o RAF no qual deseja editar os Órgãos de Execução.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    openSearchProcessNumber: function() {
        Ext._create('raf.searchprocessnumber.SearchProcessNumberWindow', {
            values: { }
        }).show();
    },

    defineDate: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            employee = selected.get('employee');
        } else {
            employee = '';
        }
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando RAF(s)...'});
        if(month && year) {
            Ext._create('raf.management.DefineDate', {
                values: {
                    month: month,
                    year: year,
                    rafGrid: this,
                }
            }).show();
        } else {
            Ext.Msg.show({
                title: 'Processar RAF',
                msg: 'Primeiro selecione o(s) RAF(s) no qual deseja agendar uma ação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getManageAction: function() {
        if(!this._manageAction){
            this._manageAction = new Ext.Button({
                xtype: 'button',
                text: 'Gerenciar RAF',
                iconCls: 'icon-core icon-core-run',
                menu: [
                    {
                        text: 'RAF',
                        iconCls: 'icon-core icon-core-edit',
                        scope: this,
                        menu: [
                            {
                                text: 'Controle',
                                iconCls: 'icon-core icon-core-reports',
                                scope: this,
                                menu: [
                                    {
                                        text: 'Criar RAF',
                                        iconCls: 'icon-core icon-core-add',
                                        scope: this,
                                        handler: function() { this.openCreateRAFWindow(); }
                                    },
                                    {
                                        text: 'Remover RAF',
                                        iconCls: 'icon-core icon-core-minus',
                                        scope: this,
                                        handler: function() { this.openDropRAFWindow(); }
                                    },
                                    '-',
                                    {
                                        text: 'Órgão de Execução',
                                        iconCls: 'icon-core icon-core-reports',
                                        scope: this,
                                        menu: [
                                            {
                                                text: 'Adicionar',
                                                iconCls: 'icon-core icon-core-add',
                                                scope: this,
                                                handler: function() { this.addWorkerlocation(); }
                                            },
                                            {
                                                text: 'Remover',
                                                iconCls: 'icon-core icon-core-minus',
                                                scope: this,
                                                handler: function() { this.delWorkerlocation(); }
                                            },
                                        ]
                                    }
                                ]
                            },
                            {
                                text: 'Liberação',
                                iconCls: 'icon-core icon-core-success',
                                scope: this,
                                menu: [
                                    {
                                        text: 'Abrir',
                                        iconCls: 'icon-raf icon-raf-open',
                                        scope: this,
                                        handler: function() { this.openRaf(); }
                                    },
                                    {
                                        text: 'Fechar',
                                        iconCls: 'icon-raf icon-raf-close',
                                        scope: this,
                                        handler: function() { this.closeRaf(); }
                                    },
                                    '-',
                                    {
                                        text: 'Abrir para todos',
                                        iconCls: 'icon-raf icon-raf-open',
                                        scope: this,
                                        handler: function() { this.openAllRaf(); }
                                    },
                                    {
                                        text: 'Fechar para todos',
                                        iconCls: 'icon-raf icon-raf-close',
                                        scope: this,
                                        handler: function() { this.closeAllRaf(); }
                                    },
                                ]
                            },
                            '-',
                            {
                                text: 'Agendar ações',
                                iconCls: 'icon-core icon-core-calendar-plus',
                                scope: this,
                                handler: function() { this.defineDate(); }
                            },
                            {
                                text: 'Comunicar via E-Doc',
                                iconCls: 'icon-raf icon-raf-manual-amount',
                                scope: this,
                                handler: function() { this.sendEdoc(); }
                            },
                        ]
                    },
                    '-',
                    {
                        text: 'Administração de dados',
                        iconCls: 'icon-core icon-core-update-manage',
                        scope: this,
                        menu: [
                            {
                                text: 'e-Proc',
                                iconCls: 'icon-core icon-core-move-fold',
                                scope: this,
                                menu: [
                                    {
                                        text: 'Importar documentos',
                                        iconCls: 'icon-core icon-core-info',
                                        scope: this,
                                          handler: function() { this.openImportEproc2AthenasWindow(); }
                                    },
                                    {
                                        text: 'Excluir documentos',
                                        iconCls: 'icon-core icon-core-error',
                                        scope: this,
                                          handler: function() { this.dropEproc2AthenasWindow(); }
                                    },
                                ]
                            },
                            {
                                text: 'e-Ext',
                                iconCls: 'icon-core icon-core-move-fold',
                                scope: this,
                                menu: [
                                    {
                                        text: 'Importar documentos',
                                        iconCls: 'icon-core icon-core-info',
                                        scope: this,
                                          handler: function() { this.openImportEExt2AthenasWindow(); }
                                    },
                                    {
                                        text: 'Excluir documentos',
                                        iconCls: 'icon-core icon-core-error',
                                        scope: this,
                                          handler: function() { this.dropEExt2AthenasWindow(); }
                                    },
                                ]
                            },
                            '-',
                            {
                                text: 'Processar RAF',
                                iconCls: 'icon-core icon-core-document-arrow',
                                scope: this,
                                  handler: function() { this.processRAF(); }
                            },
                            {
                                text: 'Recalcular SALDOS',
                                iconCls: 'icon-core icon-core-document-arrow',
                                scope: this,
                                  handler: function() { this.recalculateBalanceRAF(); }
                            },
                        ]
                    },
                    '-',
                    {
                        text: 'Pesquisar por número',
                        iconCls: 'icon-core icon-core-select',
                        scope: this,
                        handler: function() { this.openSearchProcessNumber(); }
                    },
                ]
            });
        }
        return this._manageAction;
    },

    getExtractReport: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();

        if (selected) {
            engine.mq.Report.request({
                report: '/to/mpe/raf/espelho_raf',
                waitMessage: 'Gerando os documentos...',
                params: {
                    outfile: 'extrato-raf-'+month+'/'+year+'-'+selected.get('employee_unicode'),
                    report_name: 'Espelho Mensal do RAF - '+month+'/'+year+' - '+selected.get('employee_unicode'),
                    raf: selected.get('pk'),
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para geração do relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getProcessingEExtReport: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();

        if (month && year) {
             if (selected) {
                engine.mq.Report.request({
                    report: '/to/mpe/raf/raf_eext_processamento',
                    waitMessage: 'Gerando os documentos...',
                    params: {
                        outfile: 'extrato-processamento-eext-'+month+'/'+year+'-'+selected.get('employee_matricula'),
                        report_name: 'Extrato de Processamento EExt - '+month+'/'+year+' - '+selected.get('employee_unicode'),
                        month: month,
                        year: year,
                        employee_registration: selected.get('employee_matricula'),
                    }
                });
            } else {
              engine.mq.Report.request({
                  report: '/to/mpe/raf/raf_eext_processamento',
                  waitMessage: 'Gerando os documentos...',
                  params: {
                      outfile: 'extrato-processamento-eext-'+month+'/'+year,
                      report_name: 'Extrato de Processamento EExt - '+month+'/'+year,
                      month: month,
                      year: year,
                  }
              });
            }
        } else {
            Ext.Msg.show({
              title: 'Relatórios',
              msg: 'Selecione um mês de referência para geração do Extrato de Processamento do EExt.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });

        }
    },

    getProcessingExtractReport: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();

        if (month && year) {
             if (selected) {
                engine.mq.Report.request({
                    report: '/to/mpe/raf/raf_eproc_processamento',
                    waitMessage: 'Gerando os documentos...',
                    params: {
                        outfile: 'extrato-processamento-eproc-'+month+'/'+year+'-'+selected.get('employee_matricula'),
                        report_name: 'Extrato de Processamento EProc - '+month+'/'+year+' - '+selected.get('employee_unicode'),
                        month: month,
                        year: year,
                        membro: selected.get('employee_matricula'),
                    }
                });
            } else {
              engine.mq.Report.request({
                  report: '/to/mpe/raf/raf_eproc_processamento',
                  waitMessage: 'Gerando os documentos...',
                  params: {
                      outfile: 'extrato-processamento-eproc-'+month+'/'+year,
                      report_name: 'Extrato de Processamento EProc - '+month+'/'+year,
                      month: month,
                      year: year,
                  }
              });
            }
        } else {
            Ext.Msg.show({
              title: 'Relatórios',
              msg: 'Selecione um mês de referência para geração do Extrato de Processamento do EProc.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });

        }
    },

    getProcessosSemPromotoriaReport: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;
        var selected = this.getSelectionModel().getSelected();

        if (month && year) {
             if (selected) {
                engine.mq.Report.request({
                    report: '/to/mpe/raf/raf_eproc_sem_promotoria',
                    waitMessage: 'Gerando os documentos...',
                    params: {
                        outfile: 'eproc-processos-sem-promotoria-'+month+'/'+year+'-'+selected.get('employee_matricula'),
                        report_name: 'EProc - Processos sem Promotoria - '+month+'/'+year+' - '+selected.get('employee_unicode'),
                        month: month,
                        year: year,
                        membro: selected.get('employee_matricula'),
                    }
                });
            } else {
              engine.mq.Report.request({
                  report: '/to/mpe/raf/raf_eproc_sem_promotoria',
                  waitMessage: 'Gerando os documentos...',
                  params: {
                      outfile: 'eproc-processos-sem-promotoria-'+month+'/'+year,
                      report_name: 'EProc - Processos sem Promotoria - '+month+'/'+year,
                      month: month,
                      year: year,
                  }
              });
            }
        } else {
            Ext.Msg.show({
              title: 'Relatórios',
              msg: 'Selecione um mês de referência para geração da Relação de Processos sem Promotoria',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });

        }
    },

    getProcessosPromotoriasDiversasReport: function() {
        var month = this.getParams().month;
        var year = this.getParams().year;

        if (month && year) {
            engine.mq.Report.request({
                report: '/to/mpe/raf/raf_eproc_promotorias_diversas',
                waitMessage: 'Gerando os documentos...',
                params: {
                    outfile: 'eproc-processos-promotorias-diversas-'+month+'/'+year,
                    report_name: 'EProc - Processos em Promotorias Diversas - '+month+'/'+year,
                    month: month,
                    year: year,
                }
            });
        } else {
            Ext.Msg.show({
              title: 'Relatórios',
              msg: 'Selecione um mês de referência para geração da Relação de Processos em Promotorias Diversas',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });

        }
    },

    getStatusReport: function() {
        Ext._create('raf.report.ExtractReportPeriodStatusRAF', {
            values: { }
        }).show();
    },

    getStatisticReport: function() {
        Ext._create('raf.report.StatisticRAFReport', {
            values: { }
        }).show();
    },

    getEextIn: function() {
        var selected = this.getSelectionModel().getSelected();

        if (selected) {
          console.log('implementar chamada');
            // engine.mq.Report.request({
            //     report: '/to/mpe/raf/raf_eproc_entradas',
            //     waitMessage: 'Gerando os documentos...',
            //     params: {
            //         outfile: 'eproc-entradas',
            //         report_name: 'RAF',
            //         raf: selected.get('pk'),
            //     }
            // });
        } else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getEextOut: function() {
      var selected = this.getSelectionModel().getSelected();

      if (selected) {
        console.log('implementar chamada');
          // engine.mq.Report.request({
          //     report: '/to/mpe/raf/raf_eproc_saidas',
          //     waitMessage: 'Gerando os documentos...',
          //     params: {
          //         outfile: 'eproc-saidas',
          //         report_name: 'RAF',
          //         raf: selected.get('pk'),
          //     }
          // });
      } else {
          Ext.Msg.show({
              title: 'Relatórios',
              msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
          });
      }
    },

    getEExtImport: function() {
        var selected = this.getSelectionModel().getSelected();

        if (selected) {
            engine.mq.Report.request({
                report: '/to/mpe/raf/raf_eext_import',
                waitMessage: 'Gerando os documentos...',
                params: {
                    outfile: 'eext-importacao',
                    report_name: 'RAF',
                    raf: selected.get('pk'),
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getEprocIn: function() {
        var selected = this.getSelectionModel().getSelected();

        if (selected) {
            engine.mq.Report.request({
                report: '/to/mpe/raf/raf_eproc_entradas',
                waitMessage: 'Gerando os documentos...',
                params: {
                    outfile: 'eproc-entradas',
                    report_name: 'RAF',
                    raf: selected.get('pk'),
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Relatórios',
                msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getEprocOut: function() {
      var selected = this.getSelectionModel().getSelected();

      if (selected) {
          engine.mq.Report.request({
              report: '/to/mpe/raf/raf_eproc_saidas',
              waitMessage: 'Gerando os documentos...',
              params: {
                  outfile: 'eproc-saidas',
                  report_name: 'RAF',
                  raf: selected.get('pk'),
              }
          });
      } else {
          Ext.Msg.show({
              title: 'Relatórios',
              msg: 'Primeiro selecione o Membro para poder gerar o relatório.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
          });
      }
    },

    openConsolidatedReportPeriod: function() {
        Ext._create('raf.report.ExtractReportPeriodWindow', {
            values: { }
        }).show();
    },

    openProductivityReportPeriod: function() {
        Ext._create('raf.report.ProductivityReportPeriodWindow', {
            values: { }
        }).show();
    },

    openExtractAdjustment: function() {
        Ext._create('raf.report.ExtractAdjustmentWindow', {
            values: { }
        }).show();
    },

    getReportAction: function() {
        if(!this._reportAction){
            this._reportAction = new Ext.Button({
                xtype: 'button',
                text: 'Relatórios',
                iconCls: 'icon-raf icon-raf-report',
                menu: [
                  {
                    text: 'Consolidado por Período/Membro/Lotação',
                    iconCls: 'icon-raf icon-raf-report-pdf',
                    scope: this,
                    handler: function() { this.openConsolidatedReportPeriod(); }
                  },
                  {
                    text: 'Espelho Mensal por Membro',
                    iconCls: 'icon-raf icon-raf-report-pdf',
                    scope: this,
                    handler: function() { this.getExtractReport(); }
                  },
                  {
                    text: 'Produtividade por Período/Membro/Lotação',
                    iconCls: 'icon-raf icon-raf-report-pdf',
                    scope: this,
                    handler: function() { this.openProductivityReportPeriod(); }
                  },
                  {
                    text: 'Extrato de Solicitações',
                    iconCls: 'icon-raf icon-raf-report-pdf',
                    scope: this,
                    handler: function() { this.openExtractAdjustment(); }
                  },
                  {
                    text: 'Status de Entrega por Mês',
                    iconCls: 'icon-raf icon-raf-report-pdf',
                    scope: this,
                    handler: function() { this.getStatusReport(); }
                  },
                  '-',
                  {
                    text: 'Estatísticas',
                    iconCls: 'icon-raf icon-raf-report-pdf',
                    scope: this,
                    handler: function() { this.getStatisticReport(); }
                  },
                  '-',
                  {
                      text: 'Importação e-Proc',
                      iconCls: 'icon-raf icon-raf-report-pdf',
                      scope: this,
                      menu: [
                        {
                            text: 'Relatório de Entradas',
                            iconCls: 'icon-raf icon-raf-report-pdf',
                            scope: this,
                            handler: function() { this.getEprocIn(); }
                        },
                        {
                            text: 'Relatório de Saídas',
                            iconCls: 'icon-raf icon-raf-report-pdf',
                            scope: this,
                            handler: function() { this.getEprocOut(); }
                        },
                      ]
                  },

                  {
                      text: 'Importação e-Ext',
                      iconCls: 'icon-raf icon-raf-report-pdf',
                      scope: this,
                      menu: [
                        {
                            text: 'Relatório de Importação',
                            iconCls: 'icon-raf icon-raf-report-pdf',
                            scope: this,
                            handler: function() { this.getEExtImport(); }
                        }
                      ]
                  },

                  '-',
                  {
                      text: 'Relação de Processos sem Promotoria',
                      iconCls: 'icon-raf icon-raf-report-pdf',
                      scope: this,
                      handler: function() { this.getProcessosSemPromotoriaReport(); }
                  },
                  {
                      text: 'Relação de Processos em Promotorias Diversas',
                      iconCls: 'icon-raf icon-raf-report-pdf',
                      scope: this,
                      handler: function() { this.getProcessosPromotoriasDiversasReport(); }
                  },
                  '-',
                  {
                    text: 'EPROC - Extrato de Processamento por Mês',
                    iconCls: 'icon-raf icon-raf-report-pdf',
                    scope: this,
                    handler: function() { this.getProcessingExtractReport(); }
                  },
                  {
                    text: 'EEXT - Extrato de Processamento por Mês',
                    iconCls: 'icon-raf icon-raf-report-pdf',
                    scope: this,
                    handler: function() { this.getProcessingEExtReport(); }
                  },
                ]
            });
        }
        return this._reportAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons_list', width: 70, renderer: core.rendererIconGrid, menuDisabled: true},
                    {header: 'Servidor', dataIndex: 'employee_unicode', id: 'autoExpandColumn'},
                    {header: 'Ano', dataIndex: 'year', width: 40},
                    {header: 'Mês', dataIndex: 'month', width: 40},
                    {header: 'Abertura', dataIndex: 'open_date', width: 125, renderer: Ext.util.Format.dateRenderer('d/m/Y'), menuDisabled: true, align: 'center', },
                    {header: 'Fechamento', dataIndex: 'close_date', width: 125, renderer: Ext.util.Format.dateRenderer('d/m/Y'), menuDisabled: true, align: 'center', },
                    {header: '', xtype: 'actioncolumn', align: 'center', width: 75, scope: this, menuDisabled: true,
                        items: [
                            {
                                tooltip: 'Ver histórico',
                                icon: '/'+ global.Context + '/static/images/icons/select.png',
                                scope:this,
                                handler: function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);
                                    var record = grid.getStore().getAt(row);
                                    Ext._create('raf.functionalactivityreport.HistoricRAFWindow', {
                                        params: {
                                            raf: record.data.pk,
                                            employee: record.data.employee_unicode,
                                            month: record.data.month,
                                            year: record.data.year,
                                        }
                                    }).show();
                                }
                            },
                        ]
                    }
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'raf.functionalactivityreport.Restful',
    'raf.functionalactivityreport.Grid'
);
