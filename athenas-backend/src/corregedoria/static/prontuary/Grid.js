Ext._define('corregedoria.prontuary.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.prontuary.Restful',
    restWindow: 'corregedoria.prontuary.Window',

    configOrderToolBar: ['search', 'menu', ],

    getMenuAction: function() {
        if(!this._menuAction){
            this._menuAction = new Ext.Button({
                xtype: 'button',
                text: 'Opções',
                iconCls: 'icon-crgmpe icon-crgmpe-settings',
                menu: [
                    {
                        text: 'Cadastro',
                        iconCls: 'icon-crgmpe icon-crgmpe-edit-paper',
                        scope: this,
                        menu: [
                            {
                                text: 'Dados Gerais',
                                iconCls: 'icon-crgmpe icon-crgmpe-select',
                                scope: this,
                                handler: function() {
                                    var selected = this.getSelectionModel().getSelected();
                                    if(selected) {
                                        Ext._create('corregedoria.prontuary.generaldata.Window', {
                                            values: {
                                                prontuary: selected.data.pk,
                                            },
                                        }).show();
                                    } else {
                                        Ext.Msg.show({
                                            title: 'Gestor de Prontuários',
                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                    }
                                }
                            },
                            {
                                text: 'Desempenho Funcional',
                                iconCls: 'icon-crgmpe icon-crgmpe-man-hat',
                                scope: this,
                                menu: [
                                    {
                                        text: 'Produtividade',
                                        iconCls: 'icon-crgmpe icon-crgmpe-tool',
                                        scope: this,
                                        handler: function() {
                                            Ext._create('raf.report.ProductivityReportPeriodWindow', {
                                                values: { }
                                            }).show();
                                        }
                                    },
                                    {
                                        text: 'Inspeção/Correição',
                                        iconCls: 'icon-crgmpe icon-crgmpe-house',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                Ext._create('corregedoria.prontuary.functionalperformance.inspectionlink.Manage', {
                                                    values: {
                                                        prontuary: selected.data.pk,
                                                        employee_id: selected.data.employee_id,
                                                        employee_nome: selected.data.employee_nome,
                                                    },
                                                }).show();
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Cumulação de Atividades, Cargos e Funções',
                                        iconCls: 'icon-crgmpe icon-crgmpe-users',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                Ext._create('corregedoria.prontuary.functionalperformance.listcumulation.Manage', {
                                                    values: {
                                                        prontuary: selected.data.pk,
                                                        employee_nome: selected.data.employee_nome,
                                                        grid_main: this,
                                                    },
                                                }).show();
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                ]
                            },
                            {
                                text: 'Desempenho Individual',
                                iconCls: 'icon-crgmpe icon-crgmpe-up-graph',
                                scope: this,
                                menu: [
                                    {
                                        text: 'Indicação em Lista de Remoção e Promoção',
                                        iconCls: 'icon-crgmpe icon-crgmpe-list',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var listindication = 0;
                                                // var mask = new Ext.LoadMask(this.getEl(), {msg: 'Fechando Solcitação de Ajustes...'});
                                                // mask.show();
                                                rest.checkListIndication(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                listindication = rst.listindication;
                                                                Ext._create('corregedoria.prontuary.individualperformance.listindication.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        listindication: listindication,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Participação Institucional',
                                        iconCls: 'icon-crgmpe icon-crgmpe-people-black',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var institutionalparticipation = 0;
                                                rest.checkInstitutionalParticipation(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                institutionalparticipation = rst.institutionalparticipation;
                                                                Ext._create('corregedoria.prontuary.individualperformance.institutionalparticipation.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        institutionalparticipation: institutionalparticipation,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Frequência e Aproveitamento em Cursos',
                                        iconCls: 'icon-crgmpe icon-crgmpe-edit-paper',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var coursesparticipation = 0;
                                                rest.checkCoursesParticipation(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                coursesparticipation = rst.coursesparticipation;
                                                                Ext._create('corregedoria.prontuary.individualperformance.coursesparticipation.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        coursesparticipation: coursesparticipation,
                                                                        employee_id: selected.data.employee_id,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Exercício de Cargos ou Funções',
                                        iconCls: 'icon-crgmpe icon-crgmpe-man-blue',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var exerciseinrole = 0;
                                                rest.checkExerciseInRole(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                exerciseinrole = rst.exerciseinrole;
                                                                Ext._create('corregedoria.prontuary.individualperformance.exerciseinrole.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        exerciseinrole: exerciseinrole,
                                                                        employee_id: selected.data.employee_id,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Atuação em Comarca de Particular Dificuldade',
                                        iconCls: 'icon-crgmpe icon-crgmpe-arrows',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var performanceparticulardifficulty = 0;
                                                // var mask = new Ext.LoadMask(this.getEl(), {msg: 'Fechando Solcitação de Ajustes...'});
                                                // mask.show();
                                                rest.checkListPerformanceParticularDifficulty(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                performanceparticulardifficulty = rst.performanceparticulardifficulty;
                                                                Ext._create('corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        performanceparticulardifficulty: performanceparticulardifficulty,
                                                                        employee_id: selected.data.employee_id,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Aprimoramento de Formação Jurídica e Profissional',
                                        iconCls: 'icon-crgmpe icon-crgmpe-book',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var trainingimprovement = 0;
                                                rest.checkTrainingImprovement(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                trainingimprovement = rst.trainingimprovement;
                                                                Ext._create('corregedoria.prontuary.individualperformance.trainingimprovement.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        trainingimprovement: trainingimprovement,
                                                                        employee_id: selected.data.employee_id,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Contribuição para Execução dos Programas de Atuação, Metas Institucionais e Projetos Especiais',
                                        iconCls: 'icon-crgmpe icon-crgmpe-people-blue',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var institutionalcontribution = 0;
                                                rest.checkInstitutionalContribution(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                institutionalcontribution = rst.institutionalcontribution;
                                                                Ext._create('corregedoria.prontuary.individualperformance.institutionalcontribution.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        institutionalcontribution: institutionalcontribution,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Integrar Grupo de Trabalho, Comissão ou Comitê instituídos por órgão da Administração Superior ou Auxiliar do Ministério Público, para planejamento e elaboração de planos, programas e projetos estratégicos institucionais',
                                        iconCls: 'icon-crgmpe icon-crgmpe-man-red',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var integratestrategicworkgroup = 0;
                                                rest.checkIntegrateStrategicWorkGroup(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                integratestrategicworkgroup = rst.integratestrategicworkgroup;
                                                                Ext._create('corregedoria.prontuary.individualperformance.integratestrategicworkgroup.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        integratestrategicworkgroup: integratestrategicworkgroup,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Integrar Grupo de Trabalho, Comissão ou Comitê atualmente existentes, em exercício, no âmbito da Instituição',
                                        iconCls: 'icon-crgmpe icon-crgmpe-man-black',
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var integrateworkgroup = 0;
                                                rest.checkIntegrateWorkGroup(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                integrateworkgroup = rst.integrateworkgroup;
                                                                Ext._create('corregedoria.prontuary.individualperformance.integrateworkgroup.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        integrateworkgroup: integrateworkgroup,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() {
                                                            // mask.hide();
                                                        }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                ]
                            },
                            {
                                text: 'Carreira',
                                iconCls: 'icon-crgmpe icon-crgmpe-list-papers',
                                scope: this,
                                menu: [
                                    {
                                        text: 'Movimentação',
                                        iconCls: 'icon-crgmpe icon-crgmpe-move-fold',
                                        // disabled: true,
                                        scope: this,
                                        menu: [
                                            {
                                                text: 'Promoção',
                                                iconCls: 'icon-crgmpe icon-crgmpe-man-hat',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var promotion = 0;
                                                        rest.checkPromotion(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        promotion = rst.promotion;
                                                                        Ext._create('corregedoria.prontuary.career.movement.promotion.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                promotion: promotion,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() {
                                                                    // mask.hide();
                                                                }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                            {
                                                text: 'Remoção',
                                                iconCls: 'icon-crgmpe icon-crgmpe-man-red',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var removal = 0;
                                                        rest.checkRemoval(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        removal = rst.removal;
                                                                        Ext._create('corregedoria.prontuary.career.movement.removal.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                removal: removal,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() {
                                                                    // mask.hide();
                                                                }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                            {
                                                text: 'Permuta',
                                                iconCls: 'icon-crgmpe icon-crgmpe-users',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var permutation = 0;
                                                        rest.checkPermutation(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        permutation = rst.permutation;
                                                                        Ext._create('corregedoria.prontuary.career.movement.permutation.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                permutation: permutation,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                        ]
                                    },
                                    {
                                        text: 'Designação',
                                        iconCls: 'icon-crgmpe icon-crgmpe-edition-mode',
                                        // disabled: true,
                                        scope: this,
                                        menu: [
                                            {
                                                text: 'Exercício',
                                                iconCls: 'icon-crgmpe icon-crgmpe-man-blue',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var exercise = 0;
                                                        rest.checkExercise(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        exercise = rst.exercise;
                                                                        Ext._create('corregedoria.prontuary.career.designation.exercise.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                exercise: exercise,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                            {
                                                text: 'Substituição',
                                                iconCls: 'icon-crgmpe icon-crgmpe-refresh',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var replacement = 0;
                                                        rest.checkReplacement(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        replacement = rst.replacement;
                                                                        Ext._create('corregedoria.prontuary.career.designation.replacement.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                replacement: replacement,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                            {
                                                text: 'Cumulação',
                                                iconCls: 'icon-crgmpe icon-crgmpe-list-papers',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var designationcumulation = 0;
                                                        rest.checkDesignationCumulation(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        designationcumulation = rst.designationcumulation;
                                                                        Ext._create('corregedoria.prontuary.career.designation.designationcumulation.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                designationcumulation: designationcumulation,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                            {
                                                text: 'Autos e Audiências',
                                                iconCls: 'icon-crgmpe icon-crgmpe-reports',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var partieshearins = 0;
                                                        rest.checkPartiesHearings(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        partieshearins = rst.partieshearins;
                                                                        Ext._create('corregedoria.prontuary.career.designation.partieshearings.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                partieshearins: partieshearins,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                            {
                                                text: 'Função Administrativa',
                                                iconCls: 'icon-crgmpe icon-crgmpe-list',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var administrativefunction = 0;
                                                        rest.checkAdministrativeFunction(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        administrativefunction = rst.administrativefunction;
                                                                        Ext._create('corregedoria.prontuary.career.designation.administrativefunction.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                administrativefunction: administrativefunction,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                            {
                                                text: 'Atuação Conjunta',
                                                iconCls: 'icon-crgmpe icon-crgmpe-users',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var jointaction = 0;
                                                        rest.checkJointAction(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        jointaction = rst.jointaction;
                                                                        Ext._create('corregedoria.prontuary.career.designation.jointaction.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                jointaction: jointaction,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                        ]
                                    },
                                    {
                                        text: 'Desligamento',
                                        iconCls: 'icon-crgmpe icon-crgmpe-delete',
                                        // disabled: true,
                                        scope: this,
                                        menu: [
                                            {
                                                text: 'Exoneração/Reversão',
                                                iconCls: 'icon-crgmpe icon-crgmpe-man-red',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var exoneration = 0;
                                                        rest.checkExoneration(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        exoneration = rst.exoneration;
                                                                        Ext._create('corregedoria.prontuary.career.termination.exoneration.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                exoneration: exoneration,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                            {
                                                text: 'Aposentadoria/Reversão',
                                                iconCls: 'icon-crgmpe icon-crgmpe-chronometer',
                                                // disabled: true,
                                                scope: this,
                                                handler: function() {
                                                    var selected = this.getSelectionModel().getSelected();
                                                    if(selected) {
                                                        var rest = this.factoryRestful();
                                                        var retirement = 0;
                                                        rest.checkRetirement(
                                                            {
                                                                prontuary: selected.data.pk,
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(rst) {
                                                                    if(rst.success) {
                                                                        core.invokeCallback((this.callback || {}).success);
                                                                        retirement = rst.retirement;
                                                                        Ext._create('corregedoria.prontuary.career.termination.retirement.Manage', {
                                                                            values: {
                                                                                prontuary: selected.data.pk,
                                                                                retirement: retirement,
                                                                                employee_nome: selected.data.employee_nome,
                                                                            },
                                                                        }).show();
                                                                    }
                                                                    else
                                                                        Ext.Msg.show({
                                                                            title: 'Gestor de Prontuários',
                                                                            msg: rst.message,
                                                                            icon: Ext.Msg.ERROR,
                                                                            buttons: Ext.Msg.OK
                                                                        });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function(message) {
                                                                    Ext.Msg.show({
                                                                        title: 'Gestor de Prontuários',
                                                                        msg: message,
                                                                        icon: Ext.Msg.ERROR,
                                                                        buttons: Ext.Msg.OK
                                                                    });
                                                                }
                                                            },
                                                            {
                                                                scope: this,
                                                                fn: function() { }
                                                            }
                                                        );
                                                    } else {
                                                        Ext.Msg.show({
                                                            title: 'Gestor de Prontuários',
                                                            msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                            icon: Ext.Msg.ERROR,
                                                            buttons: Ext.Msg.OK
                                                        });
                                                    }
                                                }
                                            },
                                        ]
                                    },
                                    {
                                        text: 'Afastamento/Licença',
                                        iconCls: 'icon-crgmpe icon-crgmpe-calendar-plus',
                                        // disabled: true,
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var departure = 0;
                                                rest.checkDeparture(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                departure = rst.departure;
                                                                Ext._create('corregedoria.prontuary.career.others.departure.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        departure: departure,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() { }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Disponibilidade',
                                        iconCls: 'icon-crgmpe icon-crgmpe-people-green',
                                        // disabled: true,
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var availability = 0;
                                                rest.checkAvailability(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                availability = rst.availability;
                                                                Ext._create('corregedoria.prontuary.career.others.availability.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        availability: availability,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() { }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },
                                    {
                                        text: 'Faltas e Penalidades',
                                        iconCls: 'icon-crgmpe icon-crgmpe-minus',
                                        // disabled: true,
                                        scope: this,
                                        handler: function() {
                                            var selected = this.getSelectionModel().getSelected();
                                            if(selected) {
                                                var rest = this.factoryRestful();
                                                var punishment = 0;
                                                rest.checkPunishment(
                                                    {
                                                        prontuary: selected.data.pk,
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(rst) {
                                                            if(rst.success) {
                                                                core.invokeCallback((this.callback || {}).success);
                                                                punishment = rst.punishment;
                                                                Ext._create('corregedoria.prontuary.career.others.punishment.Manage', {
                                                                    values: {
                                                                        prontuary: selected.data.pk,
                                                                        punishment: punishment,
                                                                        employee_nome: selected.data.employee_nome,
                                                                    },
                                                                }).show();
                                                            }
                                                            else
                                                                Ext.Msg.show({
                                                                    title: 'Gestor de Prontuários',
                                                                    msg: rst.message,
                                                                    icon: Ext.Msg.ERROR,
                                                                    buttons: Ext.Msg.OK
                                                                });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function(message) {
                                                            Ext.Msg.show({
                                                                title: 'Gestor de Prontuários',
                                                                msg: message,
                                                                icon: Ext.Msg.ERROR,
                                                                buttons: Ext.Msg.OK
                                                            });
                                                        }
                                                    },
                                                    {
                                                        scope: this,
                                                        fn: function() { }
                                                    }
                                                );
                                            } else {
                                                Ext.Msg.show({
                                                    title: 'Gestor de Prontuários',
                                                    msg: 'Primeiro selecione um Prontuário Individual para edição.',
                                                    icon: Ext.Msg.ERROR,
                                                    buttons: Ext.Msg.OK
                                                });
                                            }
                                        }
                                    },

                                ]
                            },
                        ]
                    },
                    '-',
                    {
                        text: 'Download',
                        iconCls: 'icon-diarias icon-arquivada',
                        disabled: true,
                        scope: this,
                        menu: [
                            {
                                text: 'Prontuário (PDF)',
                                // iconCls: 'icon-ged icon-ged-application-pdf',
                                scope: this,
                                handler: function() { }
                            },
                            '-',
                            {
                                text: 'Anexos do Prontuário (ZIP))',
                                // iconCls: 'icon-ged icon-ged-application-x-gzip',
                                scope: this,
                                handler: function() {  }
                            },
                        ]
                    },
                    '-',
                    {
                        text: 'Recarregar lista de membros',
                        iconCls: 'icon-crgmpe icon-crgmpe-reload',
                        scope: this,
                        handler: function() {
                            var rest = this.factoryRestful();
                            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Recarregando lista de membros...'});
                            mask.show();
                            rest.reloadListEmployees(
                                { },
                                {
                                    scope: this,
                                    fn: function(rst) {
                                        if(rst.success) {
                                            this.getStore().reload();
                                        }
                                        else
                                            Ext.Msg.show({
                                                title: 'Gestor de Prontuários',
                                                msg: rst.message,
                                                icon: Ext.Msg.ERROR,
                                                buttons: Ext.Msg.OK
                                            });
                                    }
                                },
                                {
                                    scope: this,
                                    fn: function(message) {
                                        Ext.Msg.show({
                                            title: 'Gestor de Prontuários',
                                            msg: message,
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                    }
                                },
                                {
                                    scope: this,
                                    fn: function() {
                                        mask.hide();
                                    }
                                }
                            );
                        }
                    },
                ]
            });
        }
        return this._menuAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    { header: '', dataIndex: 'icons', width: 60, renderer: core.rendererIconGrid, menuDisabled: true, },
                    { header: 'Matrícula', dataIndex: 'employee_matricula', width: 70, sortable: false, align: 'center', menuDisabled: true, },
                    { header: 'Nome', dataIndex: 'employee_nome', id: 'autoExpandColumn', sortable: false, menuDisabled: true, },
                ],
            });
        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                columnAction: false,
            }
        );
        corregedoria.prontuary.Grid.superclass.constructor.call(this, cfg);
    }
});
core.RestfulGrid.register(
    'corregedoria.prontuary.Restful',
    'corregedoria.prontuary.Grid'
);
