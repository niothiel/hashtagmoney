var app = angular.module('Debt', []);

app.controller('DebtCtrl', function ($scope, RestService) {
    $scope.names = [
        'Val',
        'Marty'
    ];

    $scope.name = $scope.names[0];
    $scope.owedTo = $scope.names[1];
    $scope.amount = '';
    $scope.date = new Date();
    $scope.notes = '';
    $scope.debts = null;
    $scope.pictureData = null;

    $scope.submit = function () {
        RestService.addNewDebt(
            $scope.name,
            $scope.owedTo,
            $scope.amount,
            $scope.date,
            $scope.notes,
            $scope.pictureData
        ).success(function (data) {
            $scope.debts.push(data.debt);
        });
    };

    RestService.getAllDebts().success(function (data, status) {
        $scope.debts = data.debts;
    });
});

app.service('RestService', function ($http, $q) {
    function getDate(millisecondsSinceEpoch) {
        var tzMinutes = new Date().getTimezoneOffset();
        var tzMilliseconds = tzMinutes * 60 * 1000;
        return new Date(tzMilliseconds + millisecondsSinceEpoch);
    }

    this.getAllDebts = function () {
        return $http.get('/api/debts').success(function (data) {
            for (var i = 0; i < data.debts.length; i++) {
                var debt = data.debts[i];
                debt.date = getDate(debt.date);
            }
        });
    };

    this.addNewDebt = function (name, owedTo, amount, date, notes, image) {
        try {
            amount = parseFloat(amount);
            amount = parseInt(amount * 100);
        } catch (e) {
            return $q.reject(e);
        }

        debt = {
            name: name,
            owed_to: owedTo,
            amount: amount,
            date: date.valueOf(),
            notes: notes,
            image: image
        };
        return $http.post('/api/debts', debt).success(function (data) {
            data.debt.date = getDate(data.debt.date);
        });
    }
});

app.directive('appFileReader', function($q) {
    var slice = Array.prototype.slice;

    return {
        restrict: 'A',
        require: '?ngModel',
        link: function(scope, element, attrs, ngModel) {
                if (!ngModel) return;

                ngModel.$render = function() {};

                element.bind('change', function(e) {
                    var element = e.target;

                    $q.all(slice.call(element.files, 0).map(readFile))
                        .then(function(values) {
                            if (element.multiple) ngModel.$setViewValue(values);
                            else ngModel.$setViewValue(values.length ? values[0] : null);
                        });

                    function readFile(file) {
                        var deferred = $q.defer();

                        var reader = new FileReader();
                        reader.onload = function(e) {
                            deferred.resolve(e.target.result);
                        };
                        reader.onerror = function(e) {
                            deferred.reject(e);
                        };
                        reader.readAsDataURL(file);

                        return deferred.promise;
                    }
                });
            }
    };
});