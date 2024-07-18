%%  Data preprocessing %%
%Here we import data and prep it for plotting

%time in s, position in m
%load csv files 
%{
Note - this is test data consisting of single trial, if you plan on doing
multiple trials you have to take an average and store the std;
To do that in matlab: [std_file_name, mean_file_name] = std(data_file)
-- help std can give more info --
%}
data1 = readtable('cf10_square_trial1_LH.csv'); %Only pose info
data2 = readtable('cf10_LH_square_vicon.csv'); %Time and Pose info concatenated

%data LH has no time info, so we generate a time vector
x_lh = data1{:, 1};
y_lh = data1{:, 2};
z_lh = data1{:, 3};
t_lh = (0:length(x_lh)-1)'*0.01; % time has same entries as pose 
%converting based on factor, 0.01 seconds = 10 ms

%extracting time and poses from data set 2, vicon
t_vicon = data2{:, 1}; 
x_vicon = data2{:, 2}./ 1000; %converting to same units mm to m
y_vicon = data2{:, 3}./ 1000;
z_vicon = data2{:, 4}./ 1000;

%removing duplicate timestamps from data1 and data 2/ cleaning up data
[t_lh, uniqueIdx1] = unique(t_lh);
x_lh = x_lh(uniqueIdx1);
y_lh = y_lh(uniqueIdx1);
z_lh = z_lh(uniqueIdx1);

[t_vicon, uniqueIdx2] = unique(t_vicon);
x_vicon = x_vicon(uniqueIdx2);
y_vicon = y_vicon(uniqueIdx2);
z_vicon = z_vicon(uniqueIdx2);

%% Main Processing - Interpolation followed by cross-correlation %%
%{
To goal is to find a common time range that represents both datasets, so
that you are interpolating onto a shared time vector. This is accomplished
by the cross-correlation on the y-value corresponding to each timestamp
across both datasets. We do this by identifying the time shift that
maximizes their alignment. Once time vectors are aligned, we find a common
time range where both datasets overlap in their y-values. We accomplish this 
by choosing the larger dataset't time vector as the new common time vector
and then interpolating the x, y, and z values from both datasets onto this 
time vector. In short, we minimize the differece in y values, maximzing 
their alignment using cross-correlation and perform time-shifting using 
interpolation
%}
%interpolating y-values onto a common time vector for cross-correlation
common_t_min = min(t_lh(1), t_vicon(1));
common_t_max = max(t_lh(end), t_vicon(end));
common_t = linspace(common_t_min, common_t_max, max(length(t_lh), length(t_vicon)));

y_lh_interp = interp1(t_lh, y_lh, common_t, 'linear', 'extrap');
y_vicon_interp = interp1(t_vicon, y_vicon, common_t, 'linear', 'extrap');

% Compute cross-correlation and find the lag that maximizes it
[crossCorr, lags] = xcorr(y_lh_interp, y_vicon_interp, 'coeff');
[~, maxIdx] = max(crossCorr);
timeShift = lags(maxIdx)*(common_t(2)-common_t(1));

%shifting the time vector for data2/vicon 
t_vicon_shifted = t_vicon+timeShift;

%determining the common time range after shifting
t_start = max(t_lh(1), t_vicon_shifted(1));
t_end = min(t_lh(end), t_vicon_shifted(end));

%determining common time vector based on the larger dataset
if length(t_lh) > length(t_vicon_shifted)
    common_t = t_lh(t_lh >= t_start & t_lh <= t_end);
else
    common_t = t_vicon_shifted(t_vicon_shifted >= t_start & t_vicon_shifted <= t_end);
end

% interpolating the axes that were shifted
aligned_x_lh = interp1(t_lh, x_lh, common_t, 'linear', 'extrap');
aligned_y_lh = interp1(t_lh, y_lh, common_t, 'linear', 'extrap');
aligned_z_lh = interp1(t_lh, z_lh, common_t, 'linear', 'extrap');

aligned_x_vicon = interp1(t_vicon_shifted, x_vicon, common_t, 'linear', 'extrap');
aligned_y_vicon = interp1(t_vicon_shifted, y_vicon, common_t, 'linear', 'extrap');
aligned_z_vicon = interp1(t_vicon_shifted, z_vicon, common_t, 'linear', 'extrap');

%% Plotting %%
%plots - fireworks baby!!!
figure;
subplot(3, 1, 1);
plot(common_t, aligned_x_lh, 'DisplayName', 'LH Data');
hold on;
plot(common_t, aligned_x_vicon, 'DisplayName', 'Vicon Data');
xlabel('Time [s]');
ylabel('X [m]');
grid on;
legend;
title('X trajectories');
hold off;

subplot(3, 1, 2);
plot(common_t, aligned_y_lh, 'DisplayName', 'LH Data');
hold on;
plot(common_t, aligned_y_vicon, 'DisplayName', 'Vicon Data');
xlabel('Time [s]');
ylabel('Y [m]');
title('Y trajectories');
grid on;
legend;
hold off;

subplot(3, 1, 3);
plot(common_t, aligned_z_lh, 'DisplayName', 'LH Data');
hold on;
plot(common_t, aligned_z_vicon, 'DisplayName', 'Vicon Data');
xlabel('Time [s]');
ylabel('Z [m]');
grid on;
legend;
title('Z trajectories');
hold off;
